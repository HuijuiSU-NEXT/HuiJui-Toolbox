import flet as ft
class TransitionManager:
  def __init__(self, container):
    self.c = container
    self.cur = None
  def switch(self, new, direction=1):
    if not self.cur:
      self.c.content = new
      self.cur = new
      self.c.update()
      return
    new.offset = ft.Offset(0.1 * direction, 0)
    new.opacity = 0
    self.c.content = ft.Stack([self.cur, new])
    self.cur.offset = ft.Offset(-0.1 * direction, 0)
    self.cur.opacity = 0
    self.c.update()
    new.offset = ft.Offset(0, 0)
    new.opacity = 1
    self.c.update()
    self.cur = new
