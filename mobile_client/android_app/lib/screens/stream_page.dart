import 'package:flutter/material.dart';
import 'package:android_app/settings.dart';
import 'package:mjpeg_stream/mjpeg_stream.dart';

/// Screen for live camera stream (MJPEG video feed).
class StreamPage extends StatefulWidget {
  const StreamPage({super.key});
  @override
  State<StreamPage> createState() => _StreamPageState();
}

class _StreamPageState extends State<StreamPage> {
  late String _streamUrl;

  @override
  void initState() {
    super.initState();
    // Construct the stream URL from current settings
    _streamUrl = '${Settings.localBaseUrl}/stream/video.mjpg';
  }

  @override
  void didUpdateWidget(StreamPage oldWidget) {
    super.didUpdateWidget(oldWidget);
    // If base URL changed (parent rebuilds with same StreamPage), update stream URL
    final newUrl = '${Settings.localBaseUrl}/stream/video.mjpg';
    if (_streamUrl != newUrl) {
      setState(() {
        _streamUrl = newUrl;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    // Display the MJPEG stream full-screen
    return Container(
      width: double.infinity,
      height: double.infinity,
      child: MJPEGStreamScreen(
          streamUrl: _streamUrl,
          width: 300.0,
          height: 200.0,
          fit: BoxFit.cover,
          showLiveIcon: true,
      ),
    );
  }
}
