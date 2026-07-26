# Benchmark prompts

Five realistic Persian UI briefs. Rules they follow, so the measurement stays honest:

- Written as a client would write them — **no mention of RTL, direction, digits, fonts,
  dates, or any defect the skill fixes**. Hinting at a defect would teach the baseline run
  the answer and destroy the comparison.
- Each brief naturally requires content that exercises several pain points: prices,
  phone numbers, dates, ranges, forms with email/phone fields, long Persian labels.
- Output is always a single self-contained HTML file, so both arms are scored identically.

Both arms receive the **same prompt text**. The only difference is that the skill arm is
told to read `skills/rtl-design/SKILL.md` first and follow it.

---

## P1 — user profile page

صفحهٔ پروفایل کاربر برای یک اپلیکیشن ایرانی بساز: عکس و نام کاربر، تاریخ عضویت، شمارهٔ
موبایل و ایمیل، یک فرم ویرایش اطلاعات، و کارت اشتراک فعال با تاریخ انقضا و مبلغ پرداختی.
خروجی: یک فایل `index.html` تک‌فایله با CSS داخلی، بدون فریمورک.

## P2 — sales dashboard

یک داشبورد فروش برای مدیر فروشگاه بساز: چهار کارت آمار (فروش امروز، تعداد سفارش، مشتری
جدید، نرخ بازگشت)، یک جدول ۶ سفارش آخر با شماره سفارش و تاریخ و مبلغ و وضعیت، و یک بخش
«محدودهٔ زمانی» برای فیلتر گزارش. خروجی: یک فایل `index.html` تک‌فایله با CSS داخلی.

## P3 — product detail page

صفحهٔ جزئیات یک محصول برای فروشگاه اینترنتی بساز: عنوان و امتیاز و تعداد نظرات، قیمت با
تخفیف، جدول مشخصات فنی، بازهٔ زمانی ارسال، و باکس افزودن به سبد. زیرش سه نظر کاربر با
تاریخ. خروجی: یک فایل `index.html` تک‌فایله با CSS داخلی.

## P4 — appointment booking form

فرم رزرو نوبت برای یک کلینیک بساز: انتخاب پزشک، انتخاب تاریخ و ساعت از بازه‌های موجود،
فیلدهای نام و شمارهٔ تماس و ایمیل، توضیحات تکمیلی، و خلاصهٔ رزرو با هزینهٔ ویزیت.
خروجی: یک فایل `index.html` تک‌فایله با CSS داخلی.

## P5 — account settings page

صفحهٔ تنظیمات حساب کاربری بساز: منوی کناری با چند بخش، فرم اطلاعات شخصی شامل موبایل و
ایمیل، تنظیمات اعلان‌ها، بخش امنیت با تاریخ آخرین ورود، و بخش صورتحساب با تاریخ تمدید و
مبلغ. خروجی: یک فایل `index.html` تک‌فایله با CSS داخلی.
