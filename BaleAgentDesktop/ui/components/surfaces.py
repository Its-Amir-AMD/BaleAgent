from __future__ import annotations

from io import BytesIO
from typing import Optional

from PySide6.QtCore import (
    Qt, QPoint, QPointF, QRect, QRectF, QSize, QEvent, QTimer,
    QVariantAnimation, QEasingCurve, QBuffer, QIODevice,
)
from PySide6.QtGui import (
    QColor, QPainter, QPainterPath, QLinearGradient, QRadialGradient,
    QPen, QBrush, QImage,
)
from PySide6.QtWidgets import QWidget, QFrame, QGraphicsDropShadowEffect

from ..design_tokens import LIGHT, DARK

try:
    from PIL import Image, ImageFilter
except ImportError:  # graceful fallback; run.bat installs Pillow from requirements.txt
    Image = None
    ImageFilter = None


LIQUID_VARIANTS = {"liquid", "dock"}


def _qimage_to_png_bytes(image: QImage) -> bytes:
    buffer = QBuffer()
    buffer.open(QIODevice.OpenModeFlag.WriteOnly)
    image.save(buffer, "PNG")
    data = bytes(buffer.data())
    buffer.close()
    return data


class AmbientCanvas(QWidget):
    """Pastel ambient wallpaper and cached, genuinely blurred backdrop source."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._dark = False
        self._blur_cache: dict[tuple[int, int, int, int], QImage] = {}
        self.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent, True)

    def set_dark_mode(self, dark: bool):
        dark = bool(dark)
        if self._dark != dark:
            self._dark = dark
            self._blur_cache.clear()
            self.update()

    def resizeEvent(self, event):
        self._blur_cache.clear()
        super().resizeEvent(event)

    def _paint_wallpaper(self, painter: QPainter, rect: QRectF):
        """Paint the wallpaper only (not child widgets), for both screen and blur cache."""
        w = max(1.0, rect.width())
        h = max(1.0, rect.height())

        base = QLinearGradient(rect.topLeft(), rect.bottomRight())
        if self._dark:
            base.setColorAt(0.0, QColor("#11182A"))
            base.setColorAt(0.48, QColor("#191D35"))
            base.setColorAt(1.0, QColor("#111629"))
        else:
            base.setColorAt(0.0, QColor("#F4F5FB"))
            base.setColorAt(0.52, QColor("#EAEFF8"))
            base.setColorAt(1.0, QColor("#F3EEF5"))
        painter.fillRect(rect, QBrush(base))

        # Soft, large colour fields. They remain visible through the glass and
        # become the actual backdrop image that is blurred for Liquid Glass.
        fields = [
            (0.08, 0.10, 0.70, "#A8B2FF", 78 if self._dark else 118),
            (0.91, 0.18, 0.62, "#8FDCCB", 55 if self._dark else 105),
            (0.30, 0.98, 0.75, "#E9B6D0", 48 if self._dark else 96),
            (0.88, 0.88, 0.52, "#8FC2EE", 46 if self._dark else 82),
            (0.55, 0.38, 0.30, "#C2B7F2", 24 if self._dark else 46),
        ]
        radius = max(w, h) * 0.72
        for x, y, scale, color, alpha in fields:
            gradient = QRadialGradient(
                QPointF(rect.left() + w * x, rect.top() + h * y),
                radius * scale,
            )
            center = QColor(color)
            center.setAlpha(alpha)
            edge = QColor(color)
            edge.setAlpha(0)
            gradient.setColorAt(0.0, center)
            gradient.setColorAt(0.55, QColor(center.red(), center.green(), center.blue(), alpha // 3))
            gradient.setColorAt(1.0, edge)
            painter.fillRect(rect, QBrush(gradient))

        # Quiet light ribbons add a little spatial depth without noisy texture.
        ribbon = QLinearGradient(rect.topLeft(), QPointF(rect.right(), rect.top() + h * 0.58))
        if self._dark:
            ribbon.setColorAt(0.0, QColor(255, 255, 255, 12))
            ribbon.setColorAt(0.35, QColor(194, 202, 255, 19))
            ribbon.setColorAt(0.72, QColor(255, 255, 255, 2))
            ribbon.setColorAt(1.0, QColor(255, 255, 255, 0))
        else:
            ribbon.setColorAt(0.0, QColor(255, 255, 255, 110))
            ribbon.setColorAt(0.35, QColor(255, 255, 255, 62))
            ribbon.setColorAt(0.72, QColor(255, 255, 255, 9))
            ribbon.setColorAt(1.0, QColor(255, 255, 255, 0))
        painter.fillRect(rect, QBrush(ribbon))

        veil = QLinearGradient(rect.topLeft(), QPointF(rect.left(), rect.bottom()))
        veil.setColorAt(0.0, QColor(255, 255, 255, 20 if self._dark else 65))
        veil.setColorAt(0.48, QColor(255, 255, 255, 0))
        veil.setColorAt(1.0, QColor(5, 9, 22, 24 if self._dark else 0))
        painter.fillRect(rect, QBrush(veil))

    def _make_blurred_wallpaper(self, radius: int = 22) -> QImage:
        if Image is None or ImageFilter is None:
            return QImage()
        dpr = max(1.0, float(self.devicePixelRatioF()))
        width = max(1, round(self.width() * dpr))
        height = max(1, round(self.height() * dpr))
        key = (width, height, round(dpr * 100), int(self._dark), int(radius))
        cached = self._blur_cache.get(key)
        if cached is not None:
            return cached

        source = QImage(width, height, QImage.Format.Format_RGBA8888)
        source.fill(Qt.GlobalColor.transparent)
        painter = QPainter(source)
        painter.scale(dpr, dpr)
        self._paint_wallpaper(painter, QRectF(0, 0, self.width(), self.height()))
        painter.end()

        try:
            pil_image = Image.open(BytesIO(_qimage_to_png_bytes(source))).convert("RGBA")
            blurred = pil_image.filter(ImageFilter.GaussianBlur(radius=max(1, radius * dpr)))
            output = QImage.fromData(_pil_to_png(blurred), "PNG")
            output.setDevicePixelRatio(dpr)
        except Exception:
            # The rest of the glass treatment still works as translucent material.
            return QImage()

        self._blur_cache[key] = output
        return output

    def blurred_region_for(self, widget: QWidget, radius: int = 22) -> QImage:
        """Return a DPR-aware blurred wallpaper crop for a child widget."""
        if self.width() <= 0 or self.height() <= 0 or widget.width() <= 0 or widget.height() <= 0:
            return QImage()
        source = self._make_blurred_wallpaper(radius)
        if source.isNull():
            return QImage()
        origin = widget.mapTo(self, QPoint(0, 0))
        dpr = max(1.0, float(self.devicePixelRatioF()))
        crop = QRect(
            round(origin.x() * dpr),
            round(origin.y() * dpr),
            round(widget.width() * dpr),
            round(widget.height() * dpr),
        )
        crop = crop.intersected(QRect(0, 0, source.width(), source.height()))
        if crop.isEmpty():
            return QImage()
        result = source.copy(crop)
        result.setDevicePixelRatio(dpr)
        return result

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        self._paint_wallpaper(painter, QRectF(self.rect()))
        painter.end()


def _pil_to_png(image) -> bytes:
    buffer = BytesIO()
    image.save(buffer, format="PNG", optimize=False)
    return buffer.getvalue()


class GlassPanel(QFrame):
    """A layered material surface. Only 'liquid' and 'dock' use Liquid Glass."""

    def __init__(self, parent=None, radius: int = 22, variant: str = "panel", interactive: bool = True):
        super().__init__(parent)
        self.radius = int(radius)
        self.variant = variant
        self.interactive = bool(interactive)
        self._dark = False
        self._lift = 0.0
        self._sweep = -0.5
        self._pointer_inside = False
        self._pointer_pos = QPointF(-1000, -1000)
        self._backdrop_image = QImage()
        self._filters_installed = False
        self._is_liquid = variant in LIQUID_VARIANTS

        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setMouseTracking(True)
        self.setAttribute(Qt.WidgetAttribute.WA_Hover, True)
        self.setAutoFillBackground(False)

        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(30 if self._is_liquid else 13)
        self.shadow.setOffset(0, 9 if self._is_liquid else 3)
        self.shadow.setColor(QColor(3, 8, 22, 94 if self._is_liquid else 30))
        self.setGraphicsEffect(self.shadow)

        self.lift_animation = QVariantAnimation(self)
        self.lift_animation.setDuration(210)
        self.lift_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.lift_animation.valueChanged.connect(self._set_lift)

        self.sweep_animation = QVariantAnimation(self)
        self.sweep_animation.setDuration(720)
        self.sweep_animation.setStartValue(-0.5)
        self.sweep_animation.setEndValue(1.5)
        self.sweep_animation.setEasingCurve(QEasingCurve.Type.InOutSine)
        self.sweep_animation.valueChanged.connect(self._set_sweep)

        self._backdrop_timer = QTimer(self)
        self._backdrop_timer.setSingleShot(True)
        self._backdrop_timer.setInterval(35)
        self._backdrop_timer.timeout.connect(self._refresh_backdrop)

    def set_dark_mode(self, dark: bool):
        dark = bool(dark)
        if self._dark != dark:
            self._dark = dark
            self._backdrop_image = QImage()
            self._schedule_backdrop_refresh()
        self._update_shadow()
        self.update()

    def _set_lift(self, value):
        self._lift = float(value)
        self._update_shadow()
        self.update()

    def _set_sweep(self, value):
        self._sweep = float(value)
        if self._sweep >= 1.49:
            self._sweep = -0.5
        self.update()

    def _update_shadow(self):
        if self._is_liquid:
            if self._dark:
                color = QColor(3, 7, 20, 120 + int(self._lift * 38))
            else:
                color = QColor(102, 111, 153, 48 + int(self._lift * 26))
            self.shadow.setColor(color)
            self.shadow.setBlurRadius(27 + self._lift * 18)
            self.shadow.setOffset(0, 8 + self._lift * 5)
        else:
            self.shadow.setColor(QColor(5, 10, 24, 42 if self._dark else 22))
            self.shadow.setBlurRadius(12 + self._lift * 5)
            self.shadow.setOffset(0, 3 + self._lift * 2)

    def _find_canvas(self) -> Optional[AmbientCanvas]:
        parent = self.parentWidget()
        while parent is not None:
            if isinstance(parent, AmbientCanvas):
                return parent
            parent = parent.parentWidget()
        return None

    def _schedule_backdrop_refresh(self):
        if self._is_liquid and self.isVisible():
            self._backdrop_timer.start()

    def _refresh_backdrop(self):
        if not self._is_liquid:
            return
        canvas = self._find_canvas()
        if canvas is None:
            self._backdrop_image = QImage()
        else:
            self._backdrop_image = canvas.blurred_region_for(self, radius=24 if self.variant == "dock" else 20)
        self.update()

    def _install_child_pointer_filters(self):
        if self._filters_installed or not self._is_liquid:
            return
        for child in self.findChildren(QWidget):
            child.installEventFilter(self)
            child.setMouseTracking(True)
        self._filters_installed = True

    def eventFilter(self, watched, event):
        event_type = event.type()
        if event_type in (QEvent.Type.MouseMove, QEvent.Type.Enter) and isinstance(watched, QWidget):
            try:
                local = watched.mapTo(self, event.position().toPoint()) if hasattr(event, "position") else watched.mapTo(self, QPoint(0, 0))
                self._pointer_pos = QPointF(local)
                self._pointer_inside = self.rect().contains(local)
                self.update()
            except RuntimeError:
                pass
        elif event_type == QEvent.Type.Leave:
            # Child-to-child movement is handled by the next Enter/MouseMove.
            QTimer.singleShot(30, self._clear_pointer_if_outside)
        return super().eventFilter(watched, event)

    def _clear_pointer_if_outside(self):
        from PySide6.QtGui import QCursor
        pos = self.mapFromGlobal(QCursor.pos())
        if not self.rect().contains(pos):
            self._pointer_inside = False
            self.update()

    def showEvent(self, event):
        super().showEvent(event)
        self._install_child_pointer_filters()
        self._schedule_backdrop_refresh()
        if self._is_liquid:
            self.sweep_animation.stop()
            self.sweep_animation.start()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._schedule_backdrop_refresh()

    def moveEvent(self, event):
        super().moveEvent(event)
        self._schedule_backdrop_refresh()

    def enterEvent(self, event):
        if self.interactive:
            self._pointer_inside = True
            self.lift_animation.stop()
            self.lift_animation.setStartValue(self._lift)
            self.lift_animation.setEndValue(1.0)
            self.lift_animation.start()
            if self._is_liquid:
                self.sweep_animation.stop()
                self.sweep_animation.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._pointer_inside = False
        if self.interactive:
            self.lift_animation.stop()
            self.lift_animation.setStartValue(self._lift)
            self.lift_animation.setEndValue(0.0)
            self.lift_animation.start()
        super().leaveEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
        bounds = QRectF(self.rect()).adjusted(1.0, 1.0, -1.0, -1.0)
        path = QPainterPath()
        path.addRoundedRect(bounds, self.radius, self.radius)
        painter.setClipPath(path)

        if self._is_liquid:
            self._paint_liquid_glass(painter, bounds, path)
        else:
            self._paint_content_material(painter, bounds, path)
        painter.end()

    def _paint_liquid_glass(self, painter: QPainter, bounds: QRectF, path: QPainterPath):
        dark = self._dark

        # Real Gaussian blur of the app's ambient wallpaper, cached per size/theme.
        if not self._backdrop_image.isNull():
            painter.drawImage(bounds, self._backdrop_image)
        else:
            fallback = QColor(28, 37, 62, 120) if dark else QColor(255, 255, 255, 142)
            painter.fillPath(path, QBrush(fallback))

        # The tint is intentionally light: the blurred colour field must remain visible.
        tint = QLinearGradient(bounds.topLeft(), QPointF(bounds.left() + bounds.width() * .15, bounds.bottom()))
        if dark:
            tint.setColorAt(0.0, QColor(203, 211, 255, 37))
            tint.setColorAt(.42, QColor(107, 125, 183, 28))
            tint.setColorAt(1.0, QColor(17, 25, 48, 69))
        else:
            tint.setColorAt(0.0, QColor(255, 255, 255, 112))
            tint.setColorAt(.5, QColor(244, 247, 255, 70))
            tint.setColorAt(1.0, QColor(220, 230, 248, 76))
        painter.fillPath(path, QBrush(tint))

        # Soft optical glow near the upper leading edge.
        glow = QRadialGradient(QPointF(bounds.left() + bounds.width() * .18, bounds.top() + bounds.height() * .04), bounds.width() * .78)
        glow.setColorAt(0.0, QColor(255, 255, 255, 55 if dark else 118))
        glow.setColorAt(.38, QColor(224, 231, 255, 20 if dark else 45))
        glow.setColorAt(1.0, QColor(255, 255, 255, 0))
        painter.fillPath(path, QBrush(glow))

        # Pointer-following specular reflection, sampled from child controls too.
        if self._pointer_inside:
            radius = max(105.0, min(bounds.width(), bounds.height()) * .62)
            specular = QRadialGradient(self._pointer_pos, radius)
            specular.setColorAt(0.0, QColor(255, 255, 255, 54 if dark else 80))
            specular.setColorAt(.24, QColor(214, 225, 255, 23 if dark else 42))
            specular.setColorAt(1.0, QColor(255, 255, 255, 0))
            painter.fillPath(path, QBrush(specular))

        # Specular rim: bright upper edge, cooler sides, quiet lower edge.
        rim = QLinearGradient(bounds.topLeft(), bounds.bottomLeft())
        if dark:
            rim.setColorAt(0.0, QColor(255, 255, 255, 218))
            rim.setColorAt(.10, QColor(225, 231, 255, 110))
            rim.setColorAt(.48, QColor(186, 202, 255, 57))
            rim.setColorAt(.88, QColor(153, 173, 232, 33))
            rim.setColorAt(1.0, QColor(255, 255, 255, 76))
        else:
            rim.setColorAt(0.0, QColor(255, 255, 255, 245))
            rim.setColorAt(.14, QColor(255, 255, 255, 168))
            rim.setColorAt(.55, QColor(159, 176, 219, 92))
            rim.setColorAt(1.0, QColor(255, 255, 255, 128))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(QBrush(rim), 1.35 + self._lift * .28))
        painter.drawPath(path)

        # Inner hairline and lower refractive edge.
        inner_rect = bounds.adjusted(1.5, 1.5, -1.5, -1.5)
        inner_path = QPainterPath()
        inner_path.addRoundedRect(inner_rect, max(4, self.radius - 2), max(4, self.radius - 2))
        inner_color = QColor(255, 255, 255, 38 if dark else 96)
        painter.setPen(QPen(inner_color, .75))
        painter.drawPath(inner_path)

        lower_glint = QLinearGradient(bounds.bottomLeft(), bounds.bottomRight())
        lower_glint.setColorAt(0.0, QColor(255, 255, 255, 0))
        lower_glint.setColorAt(.5, QColor(225, 232, 255, 42 if dark else 78))
        lower_glint.setColorAt(1.0, QColor(255, 255, 255, 0))
        painter.setPen(QPen(QBrush(lower_glint), .8))
        painter.drawLine(QPointF(bounds.left() + self.radius, bounds.bottom() - 1.2), QPointF(bounds.right() - self.radius, bounds.bottom() - 1.2))

        # A specular highlight travels across the edge when the surface appears/activates.
        if self._sweep > -0.49:
            x = bounds.left() + self._sweep * bounds.width()
            sweep = QLinearGradient(x - 100, bounds.top(), x + 100, bounds.bottom())
            sweep.setColorAt(0.0, QColor(255, 255, 255, 0))
            sweep.setColorAt(.48, QColor(255, 255, 255, 145 if dark else 205))
            sweep.setColorAt(.52, QColor(220, 230, 255, 105 if dark else 165))
            sweep.setColorAt(1.0, QColor(255, 255, 255, 0))
            painter.setPen(QPen(QBrush(sweep), 2.1))
            painter.drawPath(path)

    def _paint_content_material(self, painter: QPainter, bounds: QRectF, path: QPainterPath):
        """Readable content material; not every card should look like navigation glass."""
        dark = self._dark
        if self.variant == "message_out":
            top = QColor(65, 65, 110, 218) if dark else QColor(238, 238, 255, 238)
            bottom = QColor(38, 43, 78, 228) if dark else QColor(222, 227, 250, 242)
            border = QColor(192, 195, 255, 85) if dark else QColor(169, 176, 223, 145)
        elif self.variant == "message_in":
            top = QColor(31, 42, 63, 226) if dark else QColor(255, 255, 255, 238)
            bottom = QColor(24, 32, 51, 236) if dark else QColor(241, 244, 251, 242)
            border = QColor(177, 192, 229, 67) if dark else QColor(208, 215, 232, 170)
        elif self.variant in {"raised", "hero"}:
            top = QColor(37, 47, 72, 208) if dark else QColor(255, 255, 255, 235)
            bottom = QColor(26, 34, 55, 224) if dark else QColor(239, 243, 251, 241)
            border = QColor(180, 194, 231, 76) if dark else QColor(255, 255, 255, 210)
        else:  # panel / material
            top = QColor(30, 40, 62, 218) if dark else QColor(250, 251, 255, 232)
            bottom = QColor(23, 31, 50, 230) if dark else QColor(237, 241, 249, 240)
            border = QColor(165, 183, 225, 61) if dark else QColor(208, 216, 235, 170)

        fill = QLinearGradient(bounds.topLeft(), bounds.bottomRight())
        fill.setColorAt(0.0, top)
        mid = QColor(top)
        mid.setAlpha(max(0, top.alpha() - 10))
        fill.setColorAt(.52, mid)
        fill.setColorAt(1.0, bottom)
        painter.fillPath(path, QBrush(fill))

        # Very restrained top edge; content surfaces stay quiet behind text.
        highlight = QLinearGradient(bounds.topLeft(), QPointF(bounds.left(), bounds.top() + min(38, bounds.height() * .28)))
        highlight.setColorAt(0.0, QColor(255, 255, 255, 29 if dark else 100))
        highlight.setColorAt(1.0, QColor(255, 255, 255, 0))
        painter.fillPath(path, QBrush(highlight))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(border, .9 + self._lift * .15))
        painter.drawPath(path)
