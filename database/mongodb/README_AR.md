# MongoDB Database Package

هذا المجلد يحتوي على نسخة MongoDB بصيغة BSON وملف Seed لـ mongosh.

Database: `student_pipeline`
Collection: `student_profiles`
Connection: `mongodb://127.0.0.1:27017`

## أسرع طريقة باستخدام Compass

1. شغل MongoDB Server.
2. افتح Compass واتصل بـ `mongodb://127.0.0.1:27017`.
3. افتح Embedded MongoDB Shell.
4. نفذ:
   `load("C:/YOUR-PATH/student-data-pipeline/database/mongodb/create_database.js")`
5. افتح `student_pipeline` ثم `student_profiles`.

## استرجاع BSON

من PowerShell في مجلد المشروع:

`mongorestore --uri="mongodb://127.0.0.1:27017" --nsInclude="student_pipeline.student_profiles" database/mongodb/`

الملف `student_profiles.bson` يحتوي على 13 document.
