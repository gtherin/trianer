import 'package:flutter/material.dart';
import 'package:syncfusion_flutter_gauges/gauges.dart';
import 'package:syncfusion_flutter_sliders/sliders.dart';
import 'package:intl/intl.dart';

class Gauge extends StatefulWidget {
  const Gauge({Key? key}) : super(key: key);

  @override
  GaugeState createState() => GaugeState();
}

class GaugeState extends State<Gauge> {
  final double _min = 0;
  final double _max = 100;
  double _value = 20;
  DateTime _value2 = DateTime(2012, 01, 01);
  double _value3 = 30;
  @override
  Widget build(BuildContext context) {
    DateTime _min2 = DateTime(2008, 01, 01);
    DateTime _max2 = DateTime(2018, 01, 01);
    List<Widget> sliders = <Widget>[
      SfSlider.vertical(
        min: _min,
        max: _max,
        value: _value,
        interval: 20,
        showLabels: true,
        onChanged: (dynamic newValue) {
          setState(() {
            _value = newValue;
          });
        },
      ),
      SfSlider.vertical(
        min: _min2,
        max: _max2,
        value: _value2,
        interval: 2,
        showLabels: true,
        dateIntervalType: DateIntervalType.years,
        dateFormat: DateFormat.y(),
        onChanged: (dynamic newValue) {
          setState(() {
            _value2 = newValue;
          });
        },
      ),
      SfRadialGauge(axes: <RadialAxis>[
        RadialAxis(minimum: 0, maximum: 150, ranges: <GaugeRange>[
          GaugeRange(startValue: 0, endValue: 50, color: Colors.green),
          GaugeRange(startValue: 50, endValue: 100, color: Colors.orange),
          GaugeRange(startValue: 100, endValue: 150, color: Colors.red)
        ], pointers: <GaugePointer>[
          MarkerPointer(
              value: _value3,
              enableDragging: true,
              markerWidth: 30,
              markerHeight: 30,
              markerOffset: -15,
              onValueChanged: (dynamic newValue) {
                setState(() {
                  _value3 = newValue;
                });
              },
              color: Colors.indigo),
          NeedlePointer(
            enableDragging: true,
            value: _value3,
            onValueChanged: (dynamic newValue) {
              setState(() {
                _value3 = newValue;
              });
            },
          )
        ], annotations: const <GaugeAnnotation>[
          GaugeAnnotation(
              widget: Text('90.0',
                  style: TextStyle(fontSize: 25, fontWeight: FontWeight.bold)),
              angle: 90,
              positionFactor: 0.5)
        ])
      ])
    ];

    return Scaffold(body: Row(children: sliders));
    return Scaffold(
      body: Center(
          child: SfRadialGauge(
        axes: <RadialAxis>[
          RadialAxis(
              showLabels: false,
              showAxisLine: false,
              showTicks: false,
              minimum: 0,
              maximum: 99,
              ranges: <GaugeRange>[
                GaugeRange(
                    startValue: 0,
                    endValue: 33,
                    color: const Color(0xFFFE2A25),
                    label: 'Slow',
                    sizeUnit: GaugeSizeUnit.factor,
                    labelStyle:
                        GaugeTextStyle(fontFamily: 'Times', fontSize: 20),
                    startWidth: 0.65,
                    endWidth: 0.65),
                GaugeRange(
                  startValue: 33,
                  endValue: 66,
                  color: Color(0xFFFFBA00),
                  label: 'Moderate',
                  labelStyle: GaugeTextStyle(fontFamily: 'Times', fontSize: 20),
                  startWidth: 0.65,
                  endWidth: 0.65,
                  sizeUnit: GaugeSizeUnit.factor,
                ),
                GaugeRange(
                  startValue: 66,
                  endValue: 99,
                  color: Color(0xFF00AB47),
                  label: 'Fast',
                  labelStyle: GaugeTextStyle(fontFamily: 'Times', fontSize: 20),
                  sizeUnit: GaugeSizeUnit.factor,
                  startWidth: 0.65,
                  endWidth: 0.65,
                ),
              ],
              pointers: const <GaugePointer>[
                NeedlePointer(value: 60)
              ])
        ],
      )),
    );
  }
}
