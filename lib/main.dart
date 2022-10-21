import 'package:Trianer/gtore/color_helper.dart';
import 'package:flutter/material.dart';
import 'dart:io';

import 'package:webview_flutter/webview_flutter.dart';
import 'gauge.dart';
import 'anim_icon.dart';
import 'gtore/tabs_bar.dart';

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

class MainPage extends StatefulWidget {
  const MainPage({Key? key}) : super(key: key);

  @override
  MainPageState createState() => MainPageState();
}

class MainPageState extends State<MainPage> {
  String? menu = "Athlete";
  @override
  Widget build(BuildContext context) {
    Widget tabsBar = SizedBox(
        height: 70,
        width: MediaQuery.of(context).size.width,
        child: TabsBar(notifyParent: (nmenu) {
          menu = nmenu;
          setState(() {});
        }));

    List<Widget> ws = [];

    if (menu == "Athlete") {
      ws.add(Expanded(flex: 10, child: Dashboard(menu: "Paces")));
      //ws.add(Expanded(flex: 10, child: Dashboard(menu: "Transitions")));
      //ws.add(const Expanded(flex: 10, child: Dashboard(menu: "Age")));
    } else {
      return Expanded(
          flex: 10,
          child: Container(color: Colors.red, child: Column(children: ws)));
      return Column(
        children: <Widget>[
          Container(
              height: (MediaQuery.of(context).size.height),
              width: (MediaQuery.of(context).size.width),
              color: Colors.red,
              child: Column(children: ws))
        ],
      );
    }

    ws.add(Expanded(flex: 1, child: Text(menu!)));
    //ws.add(AnimatedIconDemoScreen());
    //ws.add(DatePicker.showDatePicker(context));

    Widget page = Column(
      children: ws,
      crossAxisAlignment: CrossAxisAlignment.center,
    );

    return Stack(children: [tabsBar, page]);
  }
}

void main() async {
  runApp(
    MaterialApp(
      theme: ThemeData(brightness: Brightness.light),
      //home: Scaffold(body: SafeArea(child: AppWebView())),
      home: const Scaffold(
          backgroundColor: kLightGray, body: SafeArea(child: MainPage())),
      debugShowCheckedModeBanner: false,
    ),
  );
}
