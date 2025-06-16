
class Settings {
  /// Base URL (protocol + host:port) of the Pi hub API.
//  static String localBaseUrl = "http://10.0.2.2:8000";
//  static String remoteBaseUrl = "http://10.0.2.2:8001";
  static String localBaseUrl = "http://192.168.0.107:8000";
  static String remoteBaseUrl = "http://192.168.0.107:8001";

  /// The backend‑registered Hub ID to proxy alerts, streams, etc.
  static int hubId = 1;

  /// Base path to proxy calls through the backend for the selected hub.
  static String get hubProxyBase => '$remoteBaseUrl/hubs/$hubId';
}
