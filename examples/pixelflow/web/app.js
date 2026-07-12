// Minimal WASM demo. Build with:
//   wasm-pack build --target web --features wasm
// then serve `web/` with a static server; ensure ./pkg/pixelflow.js exists.

import init, { WasmImageProcessor } from './pkg/pixelflow.js';

const W = 512, H = 512;

function synthBands(width, height, t = 0) {
  const len = width * height;
  const red = new Float32Array(len);
  const green = new Float32Array(len);
  const blue = new Float32Array(len);
  const nir = new Float32Array(len);
  for (let y = 0; y < height; y++) {
    for (let x = 0; x < width; x++) {
      const i = y * width + x;
      const xf = x / Math.max(1, width);
      const yf = y / Math.max(1, height);
      red[i] = Math.min(1, Math.max(0, 0.2 + 0.8 * xf));
      green[i] = Math.min(1, Math.max(0, 0.2 + 0.8 * yf));
      blue[i] = Math.min(1, Math.max(0, 0.5 * (1 - xf)));
      nir[i] = Math.min(1, Math.max(0, 0.6 * (1 - yf)));
      if (x > width * (0.4 + 0.05 * Math.sin(t * 0.002)) && x < width * (0.6 + 0.05 * Math.cos(t * 0.001))) {
        if ((y + Math.floor(t / 8)) % 16 === 0) { red[i] = 1.0; green[i] *= 0.3; }
      }
    }
  }
  return { red, green, blue, nir };
}

function drawRgb(canvas, rgbBytes, width, height) {
  const ctx = canvas.getContext('2d');
  const img = ctx.createImageData(width, height);
  for (let i = 0, j = 0; i < rgbBytes.length; i += 3, j += 4) {
    img.data[j + 0] = rgbBytes[i + 0];
    img.data[j + 1] = rgbBytes[i + 1];
    img.data[j + 2] = rgbBytes[i + 2];
    img.data[j + 3] = 255;
  }
  ctx.putImageData(img, 0, 0);
}

function drawGray(canvas, grayBytes, width, height) {
  const ctx = canvas.getContext('2d');
  const img = ctx.createImageData(width, height);
  for (let i = 0, j = 0; i < grayBytes.length; i += 1, j += 4) {
    const v = grayBytes[i];
    img.data[j + 0] = v;
    img.data[j + 1] = v;
    img.data[j + 2] = v;
    img.data[j + 3] = 255;
  }
  ctx.putImageData(img, 0, 0);
}

async function runDemo() {
  await init();
  const proc = new WasmImageProcessor(W, H);
  const falseCanvas = document.getElementById('falseColor');
  const fireCanvas = document.getElementById('fireMask');

  let t = 0;
  function frame() {
    const bands = synthBands(W, H, t);
    proc.load_band_data('red', bands.red);
    proc.load_band_data('green', bands.green);
    proc.load_band_data('blue', bands.blue);
    proc.load_band_data('nir', bands.nir);

    const falseColor = proc.process_false_color();
    const fireMask = proc.detect_fires();

    drawRgb(falseCanvas, falseColor, W, H);
    drawGray(fireCanvas, fireMask, W, H);

    t += 1;
    requestAnimationFrame(frame);
  }
  frame();
}

document.getElementById('startBtn').addEventListener('click', () => {
  runDemo().catch(err => console.error(err));
});

