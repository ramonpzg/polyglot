(function () {
  const az = document.getElementById("azimuth");
  const alt = document.getElementById("altitude");
  const azv = document.getElementById("azv");
  const altv = document.getElementById("altv");
  const view = document.getElementById("view");
  const status = document.getElementById("status");

  function debounced(ms, fn) {
    let t;
    return (...args) => {
      clearTimeout(t);
      t = setTimeout(() => fn(...args), ms);
    };
  }

  function connect() {
    const wsUrl =
      (location.protocol === "https:" ? "wss://" : "ws://") +
      location.host +
      "/ws";
    const ws = new WebSocket(wsUrl);
    ws.onopen = () => {
      status.textContent = "connected";
      send();
    };
    ws.onclose = () => {
      status.textContent = "disconnected, retrying…";
      setTimeout(connect, 1000);
    };
    ws.onerror = () => {
      status.textContent = "error";
    };
    ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data);
        if (msg.png) {
          view.src = "data:image/png;base64," + msg.png;
        } else if (msg.error) {
          status.textContent = "error: " + msg.error;
        }
      } catch (e) {
        console.error(e);
      }
    };

    const send = debounced(40, () => {
      azv.textContent = az.value + "°";
      altv.textContent = alt.value + "°";
      ws.readyState === WebSocket.OPEN &&
        ws.send(
          JSON.stringify({
            azimuth: Number(az.value),
            altitude: Number(alt.value),
          }),
        );
    });

    az.addEventListener("input", send);
    alt.addEventListener("input", send);
  }

  connect();
})();
