import threading, time
class Ticker:
  def __init__(self, fps=60):
    self.fps = fps
    self.running = True
    self.callbacks = []
    threading.Thread(target=self._run, daemon=True).start()
  def add(self, cb): self.callbacks.append(cb)
  def _run(self):
    last = time.time()
    while self.running:
      now = time.time()
      dt = min(now - last, 0.05)
      last = now
      for cb in self.callbacks:
        try: cb(dt)
        except: pass
      time.sleep(1/self.fps)
  def stop(self): self.running = False
