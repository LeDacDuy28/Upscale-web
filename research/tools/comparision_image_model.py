import cv2
import numpy as np
import os

def add_label_below(image, label, font_scale=0.6, thickness=1):
    """Thêm label bên dưới ảnh. In đậm nếu là 'RealDegra-ESRGAN'."""

    # Nếu ảnh là grayscale -> chuyển sang BGR
    if len(image.shape) == 2 or image.shape[2] == 1:
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

    h, w = image.shape[:2]
    space = 30
    labeled_img = np.full((h + space, w, 3), 255, dtype=np.uint8)
    labeled_img[0:h, 0:w] = image

    font = cv2.FONT_HERSHEY_SIMPLEX
    text_size = cv2.getTextSize(label, font, font_scale, thickness)[0]
    text_x = (w - text_size[0]) // 2
    text_y = h + (space + text_size[1]) // 2

    if label == "RealDegra-ESRGAN":
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                cv2.putText(labeled_img, label, (text_x + dx, text_y + dy),
                            font, font_scale, (0, 0, 0), thickness, cv2.LINE_AA)
    else:
        cv2.putText(labeled_img, label, (text_x, text_y),
                    font, font_scale, (0, 0, 0), thickness, cv2.LINE_AA)

    return labeled_img


def add_padding(img, pad_h, pad_w):
    return cv2.copyMakeBorder(img, pad_h, pad_h, pad_w, pad_w,
                               cv2.BORDER_CONSTANT, value=(255, 255, 255))

def crop_and_save_each_image(
    original_path, esrgan_path, edsr_path, realsr_path, realesrgan_path,
    crop_x, crop_y, crop_w, crop_h,
    pad_h=10, pad_w=10,
    save_dir="cropped_outputs"
):
    # Tạo thư mục nếu chưa có
    os.makedirs(save_dir, exist_ok=True)

    # Load ảnh
    img_ori = cv2.imread(original_path)
    img_esrgan = cv2.imread(esrgan_path)
    img_edsr = cv2.imread(edsr_path)
    img_realsr = cv2.imread(realsr_path)
    img_realesrgan = cv2.imread(realesrgan_path)

    # Resize các ảnh về kích thước gốc của ảnh ori
    h, w = img_ori.shape[:2]
    imgs = [ img_esrgan, img_edsr, img_realsr, img_realesrgan]
    imgs = [cv2.resize(img, (w, h)) for img in imgs]
    img_list = [img_ori] + imgs

    labels = ["Original", "ESRGAN", "EDSR", "RealSR", "RealDegra-ESRGAN"]

    for img, label in zip(img_list, labels):
        # Crop
        cropped = img[crop_y:crop_y+crop_h, crop_x:crop_x+crop_w]
        # Gắn label bên dưới
        labeled = add_label_below(cropped, label)
        # Thêm padding
        padded = add_padding(labeled, pad_h, pad_w)
        # Lưu ảnh
        out_path = os.path.join(save_dir, f"{label}_crop.png")
        cv2.imwrite(out_path, padded)
        print(f"Saved: {out_path}")

# 👉 Gọi hàm (chỉ cần đổi `save_dir` nếu bạn muốn lưu chỗ khác)
crop_and_save_each_image(
    original_path=r"D:\Download\test\RealSR(V3)\Canon\Test\4\LRx4\Canon_041.png",
    esrgan_path=r"D:\EnhanceVideo_ImageDLM\BasicSR\results\EDSR_Lx4_f256b32_DIV2K_official_RealSR(V3)\visualization\RealSR(V3)_Canon\Canon_041_EDSR_Lx4_f256b32_DIV2K_official.png",
    edsr_path=r"D:\Download\Images\Images\0041_Result.png",
    realsr_path=r"D:\EnhanceVideo_ImageDLM\BasicSR\results\RealESRGAN_x4_RealSR(V3)_Canon\visualization\RealSR(V3)_Canon\Canon_041_RealESRGAN_x4.png",
    realesrgan_path=r"D:\EnhanceVideo_ImageDLM\BasicSR\results\RealESRGAN_x4_RealSR(V3)_Canon\visualization\RealSR(V3)_Canon\Canon_041_RealESRGAN_x4.png",
    crop_x=450, crop_y=200, crop_w=420, crop_h=420,
    pad_h=10, pad_w=10,
    save_dir=r"D:\EnhanceVideo_ImageDLM\results\comare"
)
