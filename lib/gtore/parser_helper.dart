import 'package:flutter/material.dart';
import 'package:font_awesome_flutter/font_awesome_flutter.dart';

double getDouble(Map<String, dynamic> json, String field,
    {double defaultVal = 0.0}) {
  try {
    return json[field] as double;
  } catch (error) {
    try {
      return (json[field] as int).toDouble();
    } catch (error) {
      return defaultVal;
    }
  }
}

String getString(Map<String, dynamic> json, String field,
    {String defaultVal = "Unknown"}) {
  try {
    return json[field] as String;
  } catch (error) {
    return defaultVal;
  }
}

List<List<dynamic>> splitList(List<dynamic> data, {int chunkSize = 5}) {
  List<List<dynamic>> chunks = [];
  for (var i = 0; i < data.length; i += chunkSize) {
    chunks.add(data.sublist(
        i, i + chunkSize > data.length ? data.length : i + chunkSize));
  }
  return chunks;
}

IconData getIconData(String icon) {
  IconData iconData;

  if (["News", "news", "About"].contains(icon)) {
    iconData = FontAwesomeIcons.newspaper;
  } else if (["Athlete", "personRunning"].contains(icon)) {
    iconData = FontAwesomeIcons.personRunning;
  } else if (["Race", "mountainSun"].contains(icon)) {
    iconData = FontAwesomeIcons.route;
  } else if (["Performances", "flagCheckered"].contains(icon)) {
    iconData = FontAwesomeIcons.gaugeHigh;
  } else if (["Simulation", "flagCheckered"].contains(icon)) {
    iconData = FontAwesomeIcons.medal;
  } else if (["Training", "flagCheckered"].contains(icon)) {
    iconData = FontAwesomeIcons.chartColumn;
  } else if (["Risk", "wallet"].contains(icon)) {
    iconData = FontAwesomeIcons.wallet;
  } else if (["Classification", "diagramProject"].contains(icon)) {
    iconData = FontAwesomeIcons.diagramProject;
  } else if (["Fundamentals", "calculator"].contains(icon)) {
    iconData = FontAwesomeIcons.calculator;
  } else if (icon.contains("Summary")) {
    iconData = FontAwesomeIcons.alignCenter;
  } else if (icon.contains("neos")) {
    iconData = FontAwesomeIcons.neos;
  } else if (["Electricité", "Electricity", "chargingStation"].contains(icon)) {
    iconData = FontAwesomeIcons.chargingStation;
  } else if (["Calendar", "calendarDay"].contains(icon)) {
    iconData = FontAwesomeIcons.calendarDay;
  } else if (["Meteo", "cloudSunRain"].contains(icon)) {
    iconData = FontAwesomeIcons.cloudSunRain;
  } else if (["rotate", "refresh"].contains(icon)) {
    iconData = FontAwesomeIcons.rotate;
  } else if (["chevronLeft", "back"].contains(icon)) {
    iconData = FontAwesomeIcons.chevronLeft;
  } else if (["Process", "networkWired"].contains(icon)) {
    iconData = FontAwesomeIcons.networkWired;
  } else if (["STK", "Stk", "Stocks", "industry"].contains(icon)) {
    iconData = FontAwesomeIcons.industry;
  } else if (["FUT", "Fut", "Futures", "chargingStation"].contains(icon)) {
    iconData = FontAwesomeIcons.chargingStation;
  } else if (["FXR", "Fxr", "moneyBill1"].contains(icon)) {
    iconData = FontAwesomeIcons.moneyBill1;
  } else if (["ETF", "Etf", "chartBar"].contains(icon)) {
    iconData = FontAwesomeIcons.chartBar;
  } else if (["fontAwesome", "Countries"].contains(icon)) {
    iconData = FontAwesomeIcons.fontAwesome;
  } else if (["Others", "Suivis", "diceD20"].contains(icon)) {
    iconData = FontAwesomeIcons.diceD20;
  } else if (["Benchmark", "fileContract"].contains(icon)) {
    iconData = FontAwesomeIcons.fileContract;
  } else if (icon.contains("Trends")) {
    iconData = FontAwesomeIcons.thumbsUp;
  } else if (icon.contains("Predictor")) {
    iconData = FontAwesomeIcons.chartLine;
  } else if (icon.contains("Twitter")) {
    iconData = FontAwesomeIcons.twitter;
  } else if (["Reddit", "reddit"].contains(icon)) {
    iconData = FontAwesomeIcons.reddit;
  } else if (["Instruments", "shapes"].contains(icon)) {
    iconData = FontAwesomeIcons.shapes;
  } else if (["Portfolio", "chartLine", "Moves"].contains(icon)) {
    iconData = FontAwesomeIcons.chartLine;
  } else if (["Markets", "landmark"].contains(icon)) {
    iconData = FontAwesomeIcons.landmark;
  } else if (["News", "earthAmericas"].contains(icon)) {
    iconData = FontAwesomeIcons.earthAmericas;
  } else if (["Budget", "piggyBank"].contains(icon)) {
    iconData = FontAwesomeIcons.piggyBank;
  } else if (["Search", "search"].contains(icon)) {
    iconData = FontAwesomeIcons.magnifyingGlass;
  } else if (["Crypto", "btc"].contains(icon)) {
    iconData = FontAwesomeIcons.btc;
  } else if (["Edit", "pen"].contains(icon)) {
    iconData = FontAwesomeIcons.pen;
  } else if (["star", "Favorites", "Watched"].contains(icon)) {
    iconData = FontAwesomeIcons.star;
  } else if (icon.contains("solidNewspaper")) {
    iconData = FontAwesomeIcons.solidNewspaper;
  } else if (icon.contains("times")) {
    iconData = FontAwesomeIcons.xmark;
  } else if (icon.contains("plus")) {
    iconData = FontAwesomeIcons.plus;
  } else if (icon.contains("timesCircle")) {
    iconData = FontAwesomeIcons.circleXmark;
  } else if (icon.contains("plusCircle")) {
    iconData = FontAwesomeIcons.circlePlus;
  } else {
    return FontAwesomeIcons.circleXmark;
  }
  return iconData;
}
