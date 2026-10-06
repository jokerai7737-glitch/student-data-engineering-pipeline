# Student Data Integration & ETL Pipeline

## 1. Project Overview

هذا المشروع يطبق Data Engineering Pipeline لدمج بيانات الطلاب من **خمسة مصادر مختلفة**:

1. CSV
2. REST API
3. SQLite Database
4. MongoDB
5. HTML Page

كل المصادر تمر عبر المسار نفسه:

```text
Extract
   ↓
Source Validation
   ↓
Cleaning
   ↓
Source Compatibility Checks
   ↓
Integration
   ↓
Transformation
   ↓
Final Validation
   ↓
Load
   ├── final_dataset.csv
   └── rejected_records.csv
```

الهدف ليس فقط جمع البيانات، بل إظهار كيف يتعامل الـPipeline مع بيانات واقعية تحتوي على أخطاء وعدم اتساق قبل أن تصبح صالحة للتحليل أو Machine Learning.

## 2. Data Sources

### CSV
`data/raw/students.csv`

الحقول:
- `student_id`
- `student_name`
- `age`
- `major`
- `city`

توجد به أخطاء مقصودة مثل:
- Duplicate student ID.
- Missing student ID.
- Age غير صالح.
- مسافات زائدة واختلاف كتابة المدن.

### REST API
`data/raw/api_response.json`

يتم تقديمه عبر Mock REST API محلي:
`http://127.0.0.1:8765/students`

الحقول:
- `student_id`
- `gpa`
- `attendance`
- `status`

أخطاء مقصودة:
- GPA مفقود.
- GPA أكبر من 4.
- Attendance أكبر من 100.
- Duplicate student ID.
- Student ID غير موجود في CSV.

### SQLite Database
`database/students.db`

يحتوي على:
- `courses`
- `enrollments`

ويستخدم SQL JOIN لاستخراج اسم المقرر وساعاته.

أخطاء مقصودة:
- Score أكبر من 100.
- Missing student ID.

### MongoDB
MongoDB هو **قاعدة البيانات الفعلية** للمصدر الرابع، ولا توجد نسخة JSON لبيانات MongoDB داخل المشروع.

المصدر هو Collection:
`student_pipeline.student_profiles`

الحقول:
- `student_id`
- `email`
- `phone`
- `scholarship_status`

يتم الاتصال مباشرة عبر `pymongo`. يجب أن يكون خادم MongoDB قيد التشغيل قبل تنفيذ الـpipeline.

أخطاء مقصودة:
- Duplicate student ID.
- Email غير صالح.
- Phone غير صالح.
- Missing email/phone.
- Student ID غير متوافق مع CSV.

إعداد MongoDB:
1. شغل MongoDB محليًا على `mongodb://127.0.0.1:27017` أو عدل `mongodb.uri` في `config.json`.
2. نفذ `python database/init_mongodb.py` مرة واحدة لإنشاء/تعبئة Collection.
3. بيانات التهيئة الموجودة داخل `database/init_mongodb.py` تحتوي أخطاء مقصودة حتى يكتشفها الـpipeline.
4. بعد التهيئة شغل `python main.py` لتنفيذ الـpipeline.
5. يمكن تمرير الاتصال عبر متغير البيئة `MONGODB_URI` بدل القيمة الافتراضية.

### MongoDB Architecture
```text
MongoDB Server
   └── student_pipeline
       └── student_profiles
             ↓
        pymongo extraction
             ↓
          Validation
```

لا يتم تحويل بيانات MongoDB إلى JSON كقاعدة بيانات؛ JSON يظهر فقط في مصادر أخرى مثل REST API أو في ملفات الرفض عند الحاجة لتسجيل شكل السجل.

### HTML Page
`data/raw/student_advising.html`

يتم استخراج جدول HTML باستخدام `pandas.read_html`.

الحقول:
- `student_id`
- `advisor`
- `advising_score`
- `academic_warning`

أخطاء مقصودة:
- Duplicate student ID.
- Missing student ID.
- Advising score أكبر من 5.
- Missing advising score.
- مسافات إضافية في اسم المشرف.
- Student ID غير متوافق مع CSV.

يمكن بدل الملف المحلي استخدام صفحة عبر الإنترنت عن طريق ضبط:
```json
"html": {
  "use_url": true,
  "url": "https://example.com/students.html"
}
```

## 3. Data Quality Rules

- `student_id` يجب أن يكون موجودًا.
- `student_id` يجب أن يكون فريدًا في مصادر one-to-one بعد التحقق.
- `age`: من 16 إلى 80.
- `gpa`: من 0 إلى 4.
- `attendance`: من 0 إلى 100.
- `score`: من 0 إلى 100.
- `advising_score`: من 0 إلى 5.
- Email عند وجوده يجب أن يكون بصيغة صحيحة.
- Phone عند وجوده يجب أن يكون 9 أرقام ويبدأ بـ 7.
- السجلات ذات المعرف غير الموجود في CSV تسجل كـ incompatibility.
- السجلات غير الصالحة لا تدخل إلى مرحلة الدمج.

## 4. Cleaning

يتم تنفيذ:
- إزالة المسافات الزائدة.
- توحيد حالة النصوص.
- توحيد أسماء المدن.
- تحويل الأعمدة الرقمية إلى أنواع رقمية.
- توحيد semester وstatus.
- تنظيف البريد والهاتف.
- تحويل النصوص الفارغة إلى قيم قابلة للمعالجة.

## 5. Missing Values

القيم الرقمية المفقودة في:
- GPA
- Attendance
- Score
- Advising Score

تعالج باستخدام Median للقيم الصالحة بعد الدمج.

القيم النصية المفقودة تعالج بالقيمة:
`Unknown`

## 6. Integration Strategy

المفتاح المشترك بين جميع المصادر هو:
`student_id`

العلاقة:
- CSV: one-to-one
- API: one-to-one
- MongoDB: one-to-one
- HTML: one-to-one
- SQLite: one-to-many

ولهذا يمكن للطالب أن يظهر أكثر من مرة في النتيجة النهائية إذا كان لديه أكثر من مقرر.

## 7. Transformations

يتم إنشاء:
- `performance_level`
- `attendance_status`
- `advising_status`

### performance_level
- GPA < 2.0 → At Risk
- GPA >= 2.0 → Acceptable
- GPA >= 2.5 → Good
- GPA >= 3.0 → Very Good
- GPA >= 3.5 → Excellent

### attendance_status
- Attendance >= 75 → Good
- Attendance < 75 → Low

### advising_status
- Advising Score >= 4 → Strong
- Advising Score < 4 → Needs Review

## 8. Final Dataset

يحتوي الناتج النهائي على بيانات الطالب الأكاديمية والشخصية والإرشاد الأكاديمي وبيانات المقررات.

الملف:
`data/processed/final_dataset.csv`

## 9. Rejected Records

كل سجل يفشل في قواعد الجودة يحفظ في:
`data/rejected/rejected_records.csv`

ويحتوي على:
- source
- student_id
- error_reason
- record_data

وبذلك يمكن معرفة سبب رفض كل سجل وإعادة استخدامه لاحقًا بعد تصحيح البيانات.

## 10. Run

```bash
pip install -r requirements.txt
python database/init_db.py
python main.py
```

أو في Windows:

```bat
run_windows.bat
```

## 11. Tests

```bash
python -m unittest discover -s tests -v
```

الاختبارات تغطي:
- CSV extraction
- REST API extraction
- SQLite extraction
- MongoDB extraction
- HTML extraction
- Duplicate detection
- Invalid values
- Missing values
- Source compatibility
- Integration
- Final output

## 12. Outputs

- `data/processed/final_dataset.csv`
- `data/rejected/rejected_records.csv`
- `logs/pipeline.log`

## 13. Metrics

يحسب البرنامج:
- عدد سجلات CSV.
- عدد سجلات API.
- عدد سجلات SQLite.
- عدد سجلات MongoDB.
- عدد سجلات HTML.
- عدد السجلات بعد الدمج.
- عدد السجلات النهائية.
- عدد السجلات المرفوضة.
- عدد التكرارات.
- عدد القيم المفقودة بعد المعالجة.
- زمن التنفيذ.

## 14. Why This Version Is Stronger

الإصدار الجديد يوضح عمليًا مفهوم ETL على مصادر مختلفة البنية:

- CSV يمثل بيانات ملفات.
- REST API يمثل بيانات Web Service.
- SQLite يمثل قاعدة بيانات SQL.
- MongoDB يمثل NoSQL Database.
- HTML يمثل Web/Unstructured-ish tabular source.

وبذلك يصبح المشروع مثالًا عمليًا على **Heterogeneous Data Integration Pipeline** بدل أن يكون مجرد دمج CSV وAPI وقاعدة بيانات SQL.

## 13. MongoDB Database Package

لمن يريد إنشاء قاعدة MongoDB مباشرة بدل الاعتماد على بيانات داخل ملفات المشروع، يوجد مجلد:
`database/mongodb/`

ويحتوي على:
- `student_profiles.bson` — نسخة BSON من Collection.
- `create_database.js` — سكربت mongosh لإنشاء قاعدة `student_pipeline` وCollection `student_profiles` وإدخال البيانات.

الاتصال المحلي:
`mongodb://127.0.0.1:27017`

يمكن تشغيل سكربت الإنشاء من MongoDB Compass عبر الـEmbedded MongoDB Shell باستخدام `load()`، أو استرجاع ملف BSON باستخدام `mongorestore`.
