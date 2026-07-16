from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor, QPen, QBrush, QFont
from PyQt6.QtCore import Qt, QRectF, QPointF

def draw_project_icon(painter):
    # Classic yellow folder
    painter.setBrush(QBrush(QColor("#FFE082"))) # Yellow body
    painter.setPen(QPen(QColor("#F57C00"), 1.5)) # Orange border
    # Tab
    painter.drawRect(4, 6, 10, 5)
    # Main folder body
    painter.drawRect(4, 10, 24, 16)

def draw_plc_icon(painter):
    # CPU module
    painter.setBrush(QBrush(QColor("#78909C"))) # Slate gray
    painter.setPen(QPen(QColor("#37474F"), 1.5)) # Dark gray border
    painter.drawRect(6, 4, 20, 24)
    
    # LED Indicator Run (Green)
    painter.setBrush(QBrush(QColor("#4CAF50")))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawEllipse(10, 8, 4, 4)
    
    # LED Indicator Stop (Red)
    painter.setBrush(QBrush(QColor("#F44336")))
    painter.drawEllipse(10, 14, 4, 4)
    
    # Ethernet port
    painter.setBrush(QBrush(QColor("#212121")))
    painter.drawRect(12, 20, 8, 6)

def draw_db_icon(painter):
    # Yellow DB block
    painter.setBrush(QBrush(QColor("#FFE082")))
    painter.setPen(QPen(QColor("#FFA000"), 1.5))
    painter.drawRect(5, 7, 22, 20)
    
    # Text "DB"
    painter.setPen(QPen(QColor("#5D4037")))
    font = QFont("Segoe UI", 9, QFont.Weight.Bold)
    painter.setFont(font)
    painter.drawText(QRectF(5, 7, 22, 20), Qt.AlignmentFlag.AlignCenter, "DB")

def draw_scan_icon(painter):
    # Draw network connector
    painter.setBrush(QBrush(QColor("#CFD8DC")))
    painter.setPen(QPen(QColor("#455A64"), 1.5))
    painter.drawRect(4, 14, 10, 8)
    # Cable
    painter.setPen(QPen(QColor("#455A64"), 2))
    painter.drawLine(14, 18, 22, 18)
    
    # Magnifying glass
    painter.setBrush(QBrush(QColor(128, 222, 234, 150))) # Semi-transparent light blue
    painter.setPen(QPen(QColor("#00838F"), 2))
    painter.drawEllipse(14, 6, 12, 12)
    painter.drawLine(22, 14, 28, 20)

def draw_backup_icon(painter):
    # Hard Drive / File
    painter.setBrush(QBrush(QColor("#E0E0E0")))
    painter.setPen(QPen(QColor("#757575"), 1.5))
    painter.drawRect(6, 4, 20, 24)
    # Lines on document
    painter.drawLine(10, 10, 22, 10)
    painter.drawLine(10, 15, 22, 15)
    
    # Arrow down (Green)
    painter.setBrush(QBrush(QColor("#2E7D32")))
    painter.setPen(QPen(QColor("#1B5E20"), 1))
    arrow_points = [
        QPointF(16, 24),
        QPointF(11, 19),
        QPointF(14, 19),
        QPointF(14, 13),
        QPointF(18, 13),
        QPointF(18, 19),
        QPointF(21, 19)
    ]
    painter.drawPolygon(arrow_points)

def draw_restore_icon(painter):
    # Hard Drive / File
    painter.setBrush(QBrush(QColor("#E0E0E0")))
    painter.setPen(QPen(QColor("#757575"), 1.5))
    painter.drawRect(6, 4, 20, 24)
    # Lines on document
    painter.drawLine(10, 10, 22, 10)
    painter.drawLine(10, 15, 22, 15)
    
    # Arrow up (Teal / Blue)
    painter.setBrush(QBrush(QColor("#1565C0")))
    painter.setPen(QPen(QColor("#0D47A1"), 1))
    arrow_points = [
        QPointF(16, 10),
        QPointF(11, 15),
        QPointF(14, 15),
        QPointF(14, 21),
        QPointF(18, 21),
        QPointF(18, 15),
        QPointF(21, 15)
    ]
    painter.drawPolygon(arrow_points)

def draw_compare_icon(painter):
    # Left document
    painter.setBrush(QBrush(QColor("#ECEFF1")))
    painter.setPen(QPen(QColor("#90A4AE"), 1.5))
    painter.drawRect(4, 6, 11, 16)
    
    # Right document
    painter.setBrush(QBrush(QColor("#ECEFF1")))
    painter.setPen(QPen(QColor("#90A4AE"), 1.5))
    painter.drawRect(17, 6, 11, 16)
    
    # Red scan line / compare check
    painter.setPen(QPen(QColor("#D32F2F"), 1.5))
    painter.drawLine(7, 10, 12, 10)
    painter.drawLine(20, 10, 25, 10)
    painter.drawLine(7, 14, 10, 14)
    painter.drawLine(20, 14, 23, 14)
    
    # Check/X differences
    painter.setPen(QPen(QColor("#388E3C"), 2))
    painter.drawLine(8, 18, 11, 20) # checkmark left
    painter.drawLine(11, 20, 13, 17)
    
    painter.setPen(QPen(QColor("#D32F2F"), 2)) # X right
    painter.drawLine(20, 17, 24, 21)
    painter.drawLine(24, 17, 20, 21)

def draw_monitor_icon(painter):
    # Monitor screen
    painter.setBrush(QBrush(QColor("#37474F")))
    painter.setPen(QPen(QColor("#212121"), 1.5))
    painter.drawRect(4, 4, 24, 18)
    
    # Stand
    painter.setBrush(QBrush(QColor("#78909C")))
    painter.drawRect(12, 22, 8, 4)
    painter.drawRect(8, 26, 16, 2)
    
    # Green Play/Monitor symbol in screen
    painter.setBrush(QBrush(QColor("#00E676")))
    painter.setPen(Qt.PenStyle.NoPen)
    play_points = [
        QPointF(12, 8),
        QPointF(12, 18),
        QPointF(20, 13)
    ]
    painter.drawPolygon(play_points)

def draw_write_icon(painter):
    # Pencil / Edit icon
    painter.setBrush(QBrush(QColor("#FFCA28")))
    painter.setPen(QPen(QColor("#F57C00"), 1.2))
    painter.save()
    painter.translate(16, 16)
    painter.rotate(-45)
    painter.drawRect(-3, -10, 6, 16)
    
    # Pencil tip
    painter.setBrush(QBrush(QColor("#FF8A80")))
    points = [QPointF(-3, 6), QPointF(3, 6), QPointF(0, 11)]
    painter.drawPolygon(points)
    
    # Lead tip
    painter.setBrush(QBrush(QColor("#212121")))
    lead_points = [QPointF(-1.5, 9), QPointF(1.5, 9), QPointF(0, 11)]
    painter.drawPolygon(lead_points)
    painter.restore()

def draw_delete_icon(painter):
    # Red X cross
    painter.setPen(QPen(QColor("#E53935"), 3, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
    painter.drawLine(8, 8, 24, 24)
    painter.drawLine(24, 8, 8, 24)

def get_custom_icon(icon_type):
    """
    Generates a QIcon by painting custom vector graphics onto a transparent QPixmap.
    """
    pixmap = QPixmap(32, 32)
    pixmap.fill(Qt.GlobalColor.transparent)
    
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    
    if icon_type == "project":
        draw_project_icon(painter)
    elif icon_type == "plc":
        draw_plc_icon(painter)
    elif icon_type == "db":
        draw_db_icon(painter)
    elif icon_type == "scan":
        draw_scan_icon(painter)
    elif icon_type == "backup":
        draw_backup_icon(painter)
    elif icon_type == "restore":
        draw_restore_icon(painter)
    elif icon_type == "compare":
        draw_compare_icon(painter)
    elif icon_type == "monitor":
        draw_monitor_icon(painter)
    elif icon_type == "write":
        draw_write_icon(painter)
    elif icon_type == "delete":
        draw_delete_icon(painter)
    else:
        # Fallback empty document
        painter.setBrush(QBrush(QColor("white")))
        painter.setPen(QPen(QColor("black"), 1))
        painter.drawRect(8, 4, 16, 24)
        
    painter.end()
    return QIcon(pixmap)
