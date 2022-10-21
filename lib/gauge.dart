import 'package:flutter/material.dart';
import 'package:syncfusion_flutter_gauges/gauges.dart';
import 'package:syncfusion_flutter_sliders/sliders.dart';
import 'package:intl/intl.dart';
import 'package:font_awesome_flutter/font_awesome_flutter.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'wheel.dart';

class Gauge extends StatefulWidget {
  final String style;
  final double min;
  final double max;
  final double value;

  const Gauge(
      {Key? key,
      required this.min,
      required this.max,
      required this.value,
      required this.style})
      : super(key: key);

  @override
  GaugeState createState() => GaugeState();
}

class GaugeState extends State<Gauge> {
  late double _min;
  late double _max;
  late double _value;
  late DateTime _min2;
  late DateTime _max2;
  late DateTime _value2;

  Icon getIcon() {
    if (widget.style == "running") {
      return const Icon(FontAwesomeIcons.personRunning);
    } else if (widget.style == "swimming") {
      return const Icon(FontAwesomeIcons.personSwimming);
    } else if (widget.style == "cycling") {
      return const Icon(FontAwesomeIcons.personBiking);
    } else {
      return const Icon(FontAwesomeIcons.personRunning);
    }
  }

  @override
  void initState() {
    _min = widget.min;
    _max = widget.max;
    _value = widget.value;

    _min2 = DateTime(1950, 01, 01);
    _max2 = DateTime(2018, 01, 01);
    _value2 = DateTime(1990, 01, 01);

    //_value = widget._value;
    super.initState();
  }

  @override
  Widget build(BuildContext context) {
    Widget w;
    if (widget.style == "gauge") {
      w = getWidget3();
    } else {
      w = getWidget4();
    }

    return Expanded(flex: 1, child: w);
    //return Container(width: 200, child: w);
  }

  Widget getWidget1() {
    return SfSlider.vertical(
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
    );
  }

  Widget getWidget2() {
    return SfSlider.vertical(
      min: _min2,
      max: _max2,
      value: _value2,
      interval: 1,
      showLabels: true,
      dateIntervalType: DateIntervalType.years,
      dateFormat: DateFormat.y(),
      onChanged: (dynamic newValue) {
        setState(() {
          _value2 = newValue;
        });
      },
    );
  }

  Widget getWidget4() {
    return SfRadialGauge(axes: <RadialAxis>[
      RadialAxis(
          axisLineStyle: const AxisLineStyle(
            thickness: 0.1,
            thicknessUnit: GaugeSizeUnit.factor,
          ),
          pointers: <GaugePointer>[
            MarkerPointer(
                value: _value,
                enableDragging: true,
                markerWidth: 15,
                markerOffset: -5,
                markerType: MarkerType.invertedTriangle,
                onValueChanged: (dynamic newValue) {
                  setState(() {
                    _value = newValue;
                  });
                },
                color: Colors.indigo),
            RangePointer(
                value: _value,
                width: 0.1,
                sizeUnit: GaugeSizeUnit.factor,
                gradient: const SweepGradient(
                    colors: <Color>[Color(0xFFCC2B5E), Color(0xFF753A88)],
                    stops: <double>[0.25, 0.75]),
                onValueChanged: (dynamic newValue) {
                  setState(() {
                    _value = newValue;
                  });
                })
          ],
          annotations: getAnnotations()),
    ]);
  }

  Widget getWidget3() {
    List<GaugeRange> gr = [];

    Map colorsGaugeRange = {
      0.3: Colors.green,
      0.66: Colors.orange,
      1.0: Colors.red,
    };

    double pkey = 0.0;
    colorsGaugeRange.forEach((key, color) {
      double startValue = pkey * 100;
      double endValue = key * 100;

      if (_value >= endValue) {
        gr.add(GaugeRange(
          startValue: startValue,
          endValue: _value,
          color: color,
          label: 'Slow',
          sizeUnit: GaugeSizeUnit.factor,
          labelStyle: const GaugeTextStyle(fontFamily: 'Times', fontSize: 14),
        ));
      } else if (_value < startValue) {
        gr.add(GaugeRange(
            startValue: startValue,
            endValue: _value,
            color: color,
            startWidth: 0.65,
            endWidth: 0.65));
      } else if (_value > startValue && _value <= endValue) {
        gr.add(
            GaugeRange(startValue: startValue, endValue: _value, color: color));
        gr.add(GaugeRange(
            startValue: _value,
            endValue: endValue,
            color: color,
            startWidth: 0.65,
            endWidth: 0.65));
      } else {
        gr.add(GaugeRange(
            startValue: startValue, endValue: endValue, color: color));
      }
      pkey = key;
    });

    return SfRadialGauge(axes: <RadialAxis>[
      RadialAxis(
          minimum: _min,
          maximum: _max,
          ranges: gr,
          pointers: <GaugePointer>[
            MarkerPointer(
                value: _value,
                enableDragging: true,
                markerWidth: 15,
                markerOffset: -5,
                markerType: MarkerType.invertedTriangle,
                onValueChanged: (dynamic newValue) {
                  setState(() {
                    _value = newValue;
                  });
                },
                color: Colors.indigo),
            MarkerPointer(
                value: _value,
                enableDragging: true,
                markerWidth: 15,
                //markerHeight: 10,
                markerOffset: 5,
                markerType: MarkerType.triangle,
                onValueChanged: (dynamic newValue) {
                  setState(() {
                    _value = newValue;
                  });
                },
                color: Colors.indigo),
          ],
          annotations: getAnnotations())
    ]);
  }

  List<GaugeAnnotation> getAnnotations() {
    String sval = _value.round().toString();
    return <GaugeAnnotation>[
      GaugeAnnotation(
          widget: Text(sval,
              style:
                  const TextStyle(fontSize: 25, fontWeight: FontWeight.bold)),
          angle: 90,
          positionFactor: 0.0),
      GaugeAnnotation(widget: getIcon(), angle: 90, positionFactor: 0.6)
    ];
  }
}

class Dashboard extends StatefulWidget {
  final String menu;

  const Dashboard({Key? key, required this.menu}) : super(key: key);

  @override
  DashboardState createState() => DashboardState();
}

class DashboardState extends State<Dashboard> {
  @override
  Widget build(BuildContext context) {
    if (widget.menu == "Paces") {
      return Row(children: <Widget>[
        Container(width: 10),
        const Gauge(min: 10, max: 60, value: 50, style: "swimming"),
        const Gauge(min: 10, max: 60, value: 50, style: "cycling"),
        const Gauge(min: 10, max: 60, value: 50, style: "running"),
        Container(width: 10)
      ]);
    } else if (widget.menu == "Age") {
      var list = [for (int i = 40; i <= 200; i++) i];

      return Row(children: <Widget>[
        Container(width: 10),
        Looping(list: list),
        //Gauge(min: 10, max: 60, value: 50, style: "basic"),
        Container(width: 10)
      ]);
    } else {
      return Row(children: <Widget>[
        Container(width: 10),
        const Gauge(min: 10, max: 60, value: 50, style: "basic"),
        const Gauge(min: 10, max: 60, value: 50, style: "gauge"),
        const Gauge(min: 10, max: 60, value: 50, style: "gaugee"),
        Container(width: 10)
      ]);
    }

//SfDateRangePicker()
  }
}
