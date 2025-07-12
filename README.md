# 🧠 StackIt – A Minimal Q&A Forum (Odoo Hackathon 2025)

This is a complete web app built for the **Odoo Hackathon 2025**, inspired by the **StackIt** problem statement.

StackIt is a lightweight Q&A platform where users can post questions, answer others, tag topics, upvote helpful responses, and receive notifications — all wrapped in a clean and user-friendly interface.

---

## 🚀 Features Implemented

✅ User Authentication (Login/Register)  
✅ Ask Questions and Post Answers  
✅ Tags for Filtering and Categorization  
✅ Upvoting System for Answers  
✅ Rich Text Editor (bold, lists, links) for Q&A  
✅ Notification Alerts (new answers, mentions)  
✅ Admin Controls (delete/moderate questions or answers)  
✅ Clean Flask Backend with Modular Code Structure  
✅ Minimalist UI with responsive styling

---

## 🧱 Tech Stack

- **Backend**: Flask (Python)
- **Frontend**: HTML, CSS, Jinja2 Templates
- **Database**: SQLite (via SQLAlchemy ORM)
- **Rich Text Editor**: Quill.js
- **Deployment**: Local (ready for Heroku, Render, etc.)

---

## 🎥 Demo Video

📺 [Watch the full demo](https://www.loom.com/share/fed7edd8d44441199e3c5bb67b573418)

> The demo includes user registration, question posting, answering, voting, admin moderation, and notifications.

---

## 📦 Installation Instructions

```bash
git clone https://github.com/earlywinter96/stackit.git
cd stackit
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
flask run


---

## ⚠️ Note to Reviewers

Due to time constraints, this was built as a standalone web app in Flask, not as an Odoo module. However, the full functionality outlined in the StackIt problem statement is implemented, and the app is ready to be converted into an Odoo module if required.

We prioritized building a working platform with real user flows and made sure all critical user features (auth, vote, tag, notify, admin, rich text) are included and demonstrated.

---

🙌 **Thank You**

This project was a solo build by **Hemant Solanki** during the Odoo Hackathon 2025. It was a rewarding experience in rapid prototyping, backend modeling, and user-focused design.

Happy to open source, collaborate, or continue development post-event!
