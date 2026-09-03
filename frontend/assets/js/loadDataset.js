/* ============================================
   Load Real Dataset: complaints.csv
============================================ */

function loadDatasetFromCSV() {
  // Agar pehle se dataset load ho chuka hai, dobara mat karo (optional)
  // Agar har baar fresh load chahiye toh ye line hata dena:
  if (localStorage.getItem("dataset_loaded") === "true") return;

  fetch("../data/complaints.csv")
    .then(response => {
      if (!response.ok) throw new Error("CSV file not found");
      return response.text();
    })
    .then(text => {
      const lines = text.trim().split("\n").filter(line => line.trim() !== "");
      if (lines.length < 2) {
        console.warn("CSV empty ya sirf header hai");
        return;
      }

      const headers = lines[0].split(",").map(h => h.trim());
      console.log("CSV Headers:", headers);

      // Humare ticket format me map karne ke liye columns identify karo
      // Common names jo dataset me ho sakte hain:
      const col = (name) => {
        const found = headers.find(h => h.toLowerCase().includes(name));
        return found ? headers.indexOf(found) : -1;
      };

      // Index nikal lo (agar column exist karta hai)
      const idxId = col("id") > -1 ? col("id") : 0;
      const idxSubject = col("subject") > -1 ? col("subject") : (col("title") > -1 ? col("title") : 1);
      const idxDesc = col("description") > -1 ? col("description") : (col("desc") > -1 ? col("desc") : 2);
      const idxCategory = col("category") > -1 ? col("category") : (col("type") > -1 ? col("type") : 3);
      const idxPriority = col("priority") > -1 ? col("priority") : (col("urgency") > -1 ? col("urgency") : 4);
      const idxStatus = col("status") > -1 ? col("status") : 5;
      const idxAssigned = col("assigned") > -1 ? col("assigned") : (col("team") > -1 ? col("team") : 6);
      const idxUser = col("user") > -1 ? col("user") : (col("email") > -1 ? col("email") : 7);

      const rows = lines.slice(1);
      const tickets = rows.map((line, i) => {
        // CSV parsing simple (agar values me comma ho toh issue ho sakta hai, lekin basic ke liye ye chalega)
        const values = line.split(",");

        // Helper: value safely nikalna
        const get = (index) => (values[index] ? values[index].trim() : "");

        return {
          id: get(idxId) || (1000 + i + 1),
          userId: 1,
          userName: "Dataset User",
          userEmail: get(idxUser) || "user@test.com",
          subject: get(idxSubject) || "Dataset Complaint",
          description: get(idxDesc) || "Imported from complaints.csv",
          category: get(idxCategory) || "General",
          priority: get(idxPriority) || "Medium",
          status: get(idxStatus) || "Registered",
          assignedTo: get(idxAssigned) || "Customer Support",
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
          source: "Dataset CSV"
        };
      });

      // Purane demo tickets hata ke real dataset dal do
      saveTickets(tickets);
      localStorage.setItem("dataset_loaded", "true");

      console.log("✅ Dataset loaded:", tickets.length, "tickets");
      alert("Dataset loaded successfully! " + tickets.length + " complaints imported from CSV.");
    })
    .catch(err => {
      console.error("Dataset load error:", err);
      alert("Dataset file nahi mili. Pahle file data/complaints.csv me rakho. Error: " + err.message);
    });
}