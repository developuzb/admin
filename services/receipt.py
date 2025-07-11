# services/receipt.py
from PIL import Image, ImageDraw, ImageFont
import qrcode
import io


def create_invoice_image(order, amount):
    width, height = 600, 850
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)

    try:
        font_title = ImageFont.truetype("cour.ttf", 24)
        font_body = ImageFont.truetype("cour.ttf", 20)
        font_small = ImageFont.truetype("cour.ttf", 14)
    except:
        font_title = font_body = font_small = ImageFont.load_default()

    y = 40
    draw.text((width//2 - 100, y), "TEXNOSET XIZMATLARI",
              font=font_title, fill='black')
    y += 60
    draw.text((50, y), "TO‘LOV INVOYSI", font=font_title, fill='black')
    y += 40

    details = [
        f"Buyurtma: #{order['order_id']}",
        f"Xizmat: {order['service_name']}",
        f"Narxi: {amount} so‘m",
        f"Vaqt: {order['timestamp']}"
    ]
    for line in details:
        draw.text((50, y), line, font=font_body, fill='black')
        y += 30

    y += 20
    draw.text((50, y), "To‘lov kartasi:", font=font_body, fill='black')
    y += 30
    draw.text((50, y), "8600 3104 7319 9081", font=font_body, fill='black')
    y += 30
    draw.text((50, y), f"Summa: {amount} so‘m", font=font_body, fill='black')
    y += 40

    footer = "Texnoset – Ishonchli Xizmat!"
    draw.text((width//2 - 100, y), footer, font=font_small, fill='black')
    y += 20
    contact = "Aloqa: +998 77 009 71 71"
    draw.text((width//2 - 100, y), contact, font=font_small, fill='black')
    y += 30

    qr = qrcode.make("https://t.me/texnosetUZ")
    qr = qr.resize((100, 100))
    img.paste(qr, (width//2 - 50, y))
    y += 110
    draw.text((width//2 - 80, y), "Kanalimizga obuna bo‘ling!",
              font=font_small, fill='black')

    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer


def create_receipt_image(order, amount, confirmation_time):
    # Faqat "TO‘LOV CHEKI" sarlavhasi va muhr qo‘shilgan variant
    img = create_invoice_image(order, amount)
    base = Image.open(img)
    draw = ImageDraw.Draw(base)

    try:
        font_stamp = ImageFont.truetype("cour.ttf", 18)
    except:
        font_stamp = ImageFont.load_default()

    draw.text(
        (350, 700), f"✅ Tasdiq: {confirmation_time}", font=font_stamp, fill='green')
    buffer = io.BytesIO()
    base.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer
