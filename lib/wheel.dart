import 'package:flutter/material.dart';

import 'package:flutter_swiper_null_safety/flutter_swiper_null_safety.dart';

class Looping extends StatefulWidget {
  List list;

  //List<int> numbers = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9];
  //List<String> options = ['A', 'B', 'C', 'D'];

  Looping({Key? key, required this.list}) : super(key: key);

  @override
  LoopingState createState() => LoopingState();
}

class LoopingState extends State<Looping> {
  @override
  Widget build(BuildContext context) {
    List list = widget.list;
    return SizedBox(
      height: 100,
      width: 100,
      child: Swiper(
          itemCount: list.length,
          scrollDirection: Axis.horizontal,
          control: const SwiperControl(),
          itemBuilder: (BuildContext context, int index) {
            return Center(
              child: Text(
                list[index].toString(),
                style: const TextStyle(fontSize: 20.0),
              ),
            );
          }),
    );
  }
}
