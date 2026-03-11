from flask import Flask, render_template, request, jsonify
import numpy as np
from keras.models import load_model
from PIL import Image
import io
import base64

app = Flask(__name__)

model = load_model('mnist_digit_model.h5')

@app.route('/')
def index():
    return render_template('index.html')

def preprocess_digit(img_array):
    """MNIST-style preprocessing: crop, fit in 20x20 box, center by center of mass in 28x28."""
    # Threshold to remove anti-aliasing noise
    img_array = np.where(img_array > 30, img_array, 0).astype(np.float32)

    coords = np.argwhere(img_array > 0)
    if len(coords) == 0:
        return np.zeros((1, 784), dtype=np.float32)

    # Crop to bounding box of the drawn digit
    y0, x0 = coords.min(axis=0)
    y1, x1 = coords.max(axis=0)
    digit = img_array[y0:y1 + 1, x0:x1 + 1]

    # Fit into a 20x20 box (MNIST standard), preserve aspect ratio
    h, w = digit.shape
    scale = min(20.0 / h, 20.0 / w)
    new_h, new_w = max(1, int(h * scale)), max(1, int(w * scale))
    digit_img = Image.fromarray(digit).resize((new_w, new_h), Image.LANCZOS)
    digit_arr = np.array(digit_img, dtype=np.float32)

    # Compute center of mass
    ys, xs = np.nonzero(digit_arr)
    if len(xs) > 0:
        com_x = np.average(xs, weights=digit_arr[ys, xs])
        com_y = np.average(ys, weights=digit_arr[ys, xs])
    else:
        com_x, com_y = new_w / 2, new_h / 2

    # Place digit so center of mass lands at (14, 14) in 28x28
    result = np.zeros((28, 28), dtype=np.float32)
    off_x = int(round(14 - com_x))
    off_y = int(round(14 - com_y))

    sy0, sx0 = max(0, -off_y), max(0, -off_x)
    dy0, dx0 = max(0, off_y), max(0, off_x)
    ch = min(new_h - sy0, 28 - dy0)
    cw = min(new_w - sx0, 28 - dx0)
    if ch > 0 and cw > 0:
        result[dy0:dy0 + ch, dx0:dx0 + cw] = digit_arr[sy0:sy0 + ch, sx0:sx0 + cw]

    # Normalize to 0-1 (same as training: x_train / 255.0)
    result = result / 255.0
    return result.reshape(1, 784)


@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.json['image']
        image_data = base64.b64decode(data.split(',')[1])

        img = Image.open(io.BytesIO(image_data)).convert('L')
        img = img.resize((28, 28), Image.LANCZOS)
        img_array = np.array(img, dtype=np.float32)

        processed = preprocess_digit(img_array)

        prediction = model.predict(processed, verbose=0)
        predicted_class = int(np.argmax(prediction[0]))
        probabilities = [round(float(p) * 100, 2) for p in prediction[0]]

        return jsonify({
            'prediction': predicted_class,
            'confidence': probabilities[predicted_class],
            'probabilities': probabilities
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)