# 📝 Task Manager Pro

A modern, full-stack task management web app built with **Flask** and **vanilla JavaScript**.  
Plan smarter with priorities, due dates, categories, live stats, and a beautiful dashboard — no frameworks, no build step, just two files.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-2.0%2B-black?logo=flask)
![JavaScript](https://img.shields.io/badge/JavaScript-ES6-yellow?logo=javascript)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Active-success)

---

## ✨ Features

### 🎯 Task Management
- ➕ **Create tasks** with title, priority, due date, and category
- ✏️ **Inline editing** — double-click a task to rename it
- ✅ **Toggle completion** with a single click
- 🗑️ **Delete tasks** with undo support
- 🧹 **Bulk clear** all completed tasks

### 📊 Dashboard
- **Live stats cards** — Total, Active, Done, Overdue
- **Progress bar** showing completion percentage
- **Smart sorting** — incomplete first, then by priority
- **Filter tabs** — All / Active / Completed / Overdue
- **Search** across all tasks in real time

### 🎨 UX & Design
- **Dark mode** toggle (saved to localStorage)
- **Priority color-coding** — 🔴 High, 🟡 Medium, 🟢 Low
- **Overdue highlighting** on due dates
- **Category tags** with emoji
- **Toast notifications** with undo
- **Keyboard shortcuts** — `N` for new task, `/` for search
- **Fully responsive** mobile-friendly layout
- **Smooth animations** on add/remove

### 🔧 Backend
- **RESTful API** with proper HTTP methods
- **SQLite persistence** — tasks survive restarts
- **Server-side validation** on all inputs
- **XSS protection** via HTML escaping
- **Auto-initialized database** on first run

---

## 🖼️ Screenshots

> Add your own screenshots here once the app is running.
> Replace the placeholders below with real image paths or URLs.

| Light Mode | Dark Mode |
|---|---|
| ![Light](screenshots/light.png) | ![Dark](screenshots/dark.png) |

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| **Backend** | Python 3, Flask |
| **Database** | SQLite (built-in) |
| **Frontend** | HTML5, CSS3, Vanilla JavaScript (ES6) |
| **API Style** | REST |
| **Styling** | Custom CSS with CSS variables (theme-ready) |

---

## 📁 Project Structure
