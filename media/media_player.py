import win32com.client

player = win32com.client.gencache.EnsureDispatch ("WMPlayer.OCX")

class Media (object):

  def __init__ (self, filename, media):
    self.filename = filename
    self.media = media
    self.audio_bitrate = int (self._get ("AudioBitrate") or 0) or None
    self.duration = float (self._get ("Duration") or 0.0) or None
    self.audio_format = int (self._get ("FormatTag") or 0) or None
    self.video_frame_rate = int (self._get ("FrameRate") or 0) or None
    ratio_x = int (self._get ("PixelAspectRatioX") or 0) or None
    ratio_y = int (self._get ("PixelAspectRatioY") or 0) or None
    self.aspect_ratio = (ratio_x, ratio_y)
    self.title = self._get ("Title") or None
    self.video_bitrate = int (self._get ("VideoBitrate") or 0) or None
    width = int (self._get ("WM/VideoWidth") or 0) or None
    height = int (self._get ("WM/VideoHeight") or 0) or None
    self.size = (width, height)
    fourcc = int (self._get ("FourCC") or 0)
    if fourcc:
      self.video_format = "".join (chr ((fourcc >> (8 * i)) & 0xff) for i in range (4))
    else:
      self.video_format = None

  def __getitem__ (self, attr):
    return self._get (attr)

  def __getattr__ (self, attr):
    return self._get (attr)

  def _get (self, attr):
    return self.media.getItemInfo (attr)
