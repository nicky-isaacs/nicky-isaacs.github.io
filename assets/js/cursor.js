(() => {
  const dot = document.createElement('div');
  dot.className = 'cursor';
  const trail = document.createElement('div');
  trail.className = 'cursor cursor--trail';
  document.body.appendChild(dot);
  document.body.appendChild(trail);

  let mx = -100, my = -100;
  let tx = -100, ty = -100;

  document.addEventListener('mousemove', e => {
    mx = e.clientX;
    my = e.clientY;
    dot.style.left = mx + 'px';
    dot.style.top  = my + 'px';
  });

  const lerp = (a, b, t) => a + (b - a) * t;

  const tick = () => {
    tx = lerp(tx, mx, 0.14);
    ty = lerp(ty, my, 0.14);
    trail.style.left = tx + 'px';
    trail.style.top  = ty + 'px';
    requestAnimationFrame(tick);
  };
  tick();

  document.addEventListener('mouseleave', () => {
    dot.style.opacity = '0';
    trail.style.opacity = '0';
  });
  document.addEventListener('mouseenter', () => {
    dot.style.opacity = '1';
    trail.style.opacity = '1';
  });
})();
