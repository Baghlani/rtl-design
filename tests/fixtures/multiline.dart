// چیدمان چندخطی — نمونه تست
Container(
  padding: EdgeInsets.only(
    left: 8,
    top: 4,
  ),
);

Positioned(
  right: 0,
  child: Icon(Icons.star),
);

// درست: نسخه‌ی جهت‌دار نباید فلگ شود
Container(
  padding: EdgeInsetsDirectional.only(
    start: 8,
    top: 4,
  ),
);

PositionedDirectional(
  end: 0,
  child: Icon(Icons.star),
);
