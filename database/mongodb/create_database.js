// MongoDB seed script for the Student Data Pipeline project.
// Creates: student_pipeline.student_profiles
// The data intentionally contains quality errors for the ETL pipeline.

const databaseName = "student_pipeline";
const collectionName = "student_profiles";

const target = db.getSiblingDB(databaseName);

// Recreate the collection so the seed is repeatable.
target.getCollection(collectionName).drop();

const documents = [
  { student_id: 1001, email: "ahmed.ali@example.com", phone: "771234567", scholarship_status: "None" },
  { student_id: 1002, email: "sara.mohammed@example.com", phone: "772345678", scholarship_status: "Eligible" },
  { student_id: 1003, email: "omar.hassan@example.com", phone: "773456789", scholarship_status: "None" },
  { student_id: 1004, email: null, phone: "774567890", scholarship_status: "Eligible" },
  { student_id: 1005, email: "yousef_at_example.com", phone: "775678901", scholarship_status: "Eligible" },
  { student_id: 1006, email: "maryam.ahmed@example.com", phone: "12345", scholarship_status: "None" },
  { student_id: 1008, email: "noura.ali@example.com", phone: " 776789012 ", scholarship_status: " active " },
  { student_id: 1009, email: "fahad.musa@example.com", phone: "777890123", scholarship_status: "None" },
  { student_id: 1009, email: "fahad.duplicate@example.com", phone: "777890123", scholarship_status: "None" },
  { student_id: 1010, email: "huda.salem@example.com", phone: null, scholarship_status: "None" },
  { student_id: 1011, email: "ali.nasser@example.com", phone: "778901234", scholarship_status: "Eligible" },
  { student_id: 1012, email: "rawan.saleh@example.com", phone: "779012345", scholarship_status: "None" },
  { student_id: 9998, email: "extra.profile@example.com", phone: "771111111", scholarship_status: "None" }
];

target.getCollection(collectionName).insertMany(documents);

print(`Created ${databaseName}.${collectionName}`);
print(`Documents: ${target.getCollection(collectionName).countDocuments()}`);
print("Sample:");
target.getCollection(collectionName).find({}, { _id: 0 }).limit(5).forEach(doc => printjson(doc));
