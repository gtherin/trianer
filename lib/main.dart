import 'package:flutter/material.dart';
import 'dart:io';

import 'package:webview_flutter/webview_flutter.dart';
import 'gauge.dart';

class AppWebView extends StatefulWidget {
  const AppWebView({Key? key}) : super(key: key);

  @override
  AppWebViewState createState() => AppWebViewState();
}

class AppWebViewState extends State<AppWebView> {
  @override
  void initState() {
    super.initState();
    if (Platform.isAndroid) WebView.platform = AndroidWebView();
  }

  @override
  Widget build(BuildContext context) {
    return const WebView(
      initialUrl: "https://fathomless-brook-99194.herokuapp.com/",
      javascriptMode: JavascriptMode.unrestricted,
    );
  }
}

void main() async {
  runApp(
    MaterialApp(
      theme: ThemeData(
          //scaffoldBackgroundColor: Color.fromARGB(0, 248, 0, 9),
          ),
      //home: Scaffold(body: SafeArea(child: AppWebView())),
      home: const Scaffold(body: SafeArea(child: Gauge())),
      debugShowCheckedModeBanner: false,
    ),
  );
}
