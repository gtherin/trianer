import 'package:flutter/material.dart';

class AnimatedIconDemoScreen extends StatefulWidget {
  const AnimatedIconDemoScreen({Key? key}) : super(key: key);

  @override
  _AnimatedIconDemoScreenState createState() => _AnimatedIconDemoScreenState();
}

class _AnimatedIconDemoScreenState extends State<AnimatedIconDemoScreen>
    with SingleTickerProviderStateMixin {
  late AnimationController _animationController;
  // New: icon states: show menu vs. show close.
  bool isShowingMenu = false;

  @override
  void initState() {
    super.initState();

    _animationController =
        AnimationController(vsync: this, duration: const Duration(milliseconds: 500));
  }

  @override
  void dispose() {
    _animationController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Center(
      // New: Wrap icon to handle onTap event
      child: InkWell(
        child: AnimatedIcon(
          size: 100,
          color: Colors.blue,
          icon: AnimatedIcons.arrow_menu,
          progress: _animationController,
        ),
        // New: handle onTap event
        onTap: () {
          // Update the state
          isShowingMenu = !isShowingMenu;
          if (isShowingMenu) {
            // Trigger animation (start: close -> menu)
            _animationController.forward();
          } else {
            // Trigger animation (revert: menu -> close)
            _animationController.reverse();
          }
        },
      ),
    );
  }
}
