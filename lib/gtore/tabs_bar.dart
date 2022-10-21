import 'package:flutter/material.dart';
import 'color_helper.dart';
import 'parser_helper.dart';

// ignore: must_be_immutable
class TabsBarButton extends StatefulWidget {
  String pickedValue;
  final Function(String pickedValue) notifyParent;
  final List<String> choices;
  final Color activeColor;
  final Color passiveColor;
  final String style;

  TabsBarButton(
      {Key? key,
      required this.pickedValue,
      required this.notifyParent,
      required this.choices,
      this.activeColor = kGray,
      this.passiveColor = kLightGray,
      this.style = "tab"})
      : super(key: key);

  @override
  _ThemeButtonWidgetWidgetState createState() =>
      _ThemeButtonWidgetWidgetState();
}

class _ThemeButtonWidgetWidgetState extends State<TabsBarButton> {
  String? pickedValue;

  bool isActive(String selectedValue) {
    return pickedValue == selectedValue;
  }

  Color getColor(String selectedValue) {
    return isActive(selectedValue) ? widget.activeColor : widget.passiveColor;
  }

  @override
  void initState() {
    pickedValue = widget.pickedValue;
    super.initState();
  }

  void changeState({String? pickedValue}) {
    setState(() {
      this.pickedValue = pickedValue;
      widget.notifyParent(pickedValue!);
    });
  }

  void onPressedHandler(String instrsPool) {
    changeState(pickedValue: instrsPool);
  }

  Widget getIcon(String icon) {
    IconData? iconData = getIconData(icon);

    if (iconData == getIconData("timesCircle") || widget.style == "gzoom") {
      return Text(icon);
    }

    if (widget.style == "editable") {
      return Row(
          children: [Icon(iconData), const SizedBox(width: 5), Text(icon)]);
    }

    return (icon == pickedValue! || widget.style == "split_verbose")
        ? Row(children: [Icon(iconData), const SizedBox(width: 5), Text(icon)])
        : Icon(iconData);
  }

  @override
  Widget build(BuildContext context) {
    List<Widget> ws = [];

    for (var choice in widget.choices) {
      Widget child = getIcon(choice);

      ButtonStyle activeStyle = ElevatedButton.styleFrom(
        backgroundColor: Colors.grey[300],
        elevation: 0,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(50.0),
        ),
      );
      ButtonStyle passiveStyle = ElevatedButton.styleFrom(
        backgroundColor: getColor(choice),
        elevation: 0,
      );

      ws.add(ElevatedButton(
        style: (choice == pickedValue || widget.style == "editable")
            ? activeStyle
            : passiveStyle,
        onPressed: () => onPressedHandler(choice),
        child: child,
      ));
    }

    if (["editable", "split", "split_verbose"].contains(widget.style)) {
      int chunkSize =
          (["editable", "split_verbose"].contains(widget.style)) ? 3 : 5;

      List<List<dynamic>> sws = splitList(ws, chunkSize: chunkSize);
      List<Widget> chunks = [];
      for (var swi in sws) {
        chunks.add(SizedBox(
            height: 30,
            child: ListView(
                physics: const BouncingScrollPhysics(),
                padding: const EdgeInsets.all(1.0),
                addAutomaticKeepAlives: false,
                addRepaintBoundaries: false,
                scrollDirection: Axis.horizontal,
                children: swi as List<Widget>)));
      }

      Widget child = Column(
          crossAxisAlignment: CrossAxisAlignment.start, children: chunks);
      return Container(
          height: 30 * sws.length.toDouble(),
          margin: const EdgeInsets.only(top: 16, bottom: 16),
          child: child);
    }

    Widget child = ListView.builder(
        physics: const BouncingScrollPhysics(),
        padding: const EdgeInsets.all(1.0),
        addAutomaticKeepAlives: false,
        addRepaintBoundaries: false,
        scrollDirection: Axis.horizontal,
        itemCount: ws.length,
        itemBuilder: (context, index) => ws[index]);

    if (widget.style == "gzoom") {
      return Container(height: 15, alignment: Alignment.topRight, child: child);
    } else {
      return Container(
          height: 30,
          margin: const EdgeInsets.only(top: 16, bottom: 16),
          child: child);
    }
  }
}

class TabsBar extends StatefulWidget {
  final Function(String pickedValue) notifyParent;
  const TabsBar({Key? key, required this.notifyParent}) : super(key: key);

  @override
  _TabsBarState createState() => _TabsBarState();
}

class _TabsBarState extends State<TabsBar> {
  String instrsPool = "Nope";
  String theme = "Athlete";

  @override
  Widget build(BuildContext context) {
    List<Widget> ws = [
      TabsBarButton(
          pickedValue: theme,
          choices: const <String>[
            "Athlete",
            "Race",
            "Performances",
            "Simulation",
            "Training"
          ],
          style: "split",
          notifyParent: (theme) {
            this.theme = theme;
            setState(() {
              widget.notifyParent(theme);
            });
          })
    ];

    return Expanded(flex: 1, child: Column(children: ws));
  }
}
