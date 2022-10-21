import 'package:flutter/material.dart';

const kPrimaryStreamlitColor = Color(0xFFf63366);
const kSecondaryStreamlitColor = Color(0xFFf0f2f6);
const kBlackStreamlitColor = Color(0xFF262730);
const kYellowStreamlitColor = Color(0xFFfffd80);
const kWhiteStreamlitColor = Color(0xFFffffff);

const kbackgroundColor = kSecondaryStreamlitColor;
const ksecondaryBackgroundColor = kSecondaryStreamlitColor;

const kNegativeColor = Color(0xFFF44336);
const kPositiveColor = Color(0XFF17a862);

//const kTransparentWhite = Color(0X88ffffff);
const kLightGray = kSecondaryStreamlitColor;
//const kLighterGray = Color(0XFF898989);
//const kLGray = Color(0XFF999999);
const kGray = kPrimaryStreamlitColor;
const kLightBlack = Color(0XFF181818);
//const kBlack = Color(0XFF0e0e0e);

//const kTextLightGray = kLightGray;
//const kTileColor = kLGray;
//const kScaffoldBackground = kLightGray;

Color determineColorBasedOnChange(double change) {
  return change < 0 ? kNegativeColor : kPositiveColor;
}

TextStyle determineTextStyleBasedOnChange(double change) {
  if (change == 0) {
    return kNeutralChange;
  }
  return change < 0 ? kNegativeChange : kPositiveChange;
}

const TextStyle kPositiveChange =
    TextStyle(color: kPositiveColor, fontSize: 16, fontWeight: FontWeight.w800);

const TextStyle kNegativeChange =
    TextStyle(color: kNegativeColor, fontSize: 16, fontWeight: FontWeight.w800);

const TextStyle kNeutralChange =
    TextStyle(color: kGray, fontSize: 16, fontWeight: FontWeight.w800);

/// This is the common border radious of all the containers in the app.
const kStandatBorder = BorderRadius.all(Radius.circular(12));

/// This border is slightly more sharp than the standard boder.
const kSharpBorder = BorderRadius.all(Radius.circular(2));

/// This is the common text styling for a subtile.
const kSubtitleStyling =
    TextStyle(color: kGray, fontSize: 24, fontWeight: FontWeight.w800);

const kInstrumentScreenSectionTitle =
    TextStyle(fontSize: 24, fontWeight: FontWeight.bold);
