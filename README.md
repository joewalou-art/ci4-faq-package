# CI4 FAQ Package

Modern, responsive FAQ system for CodeIgniter 4.7 with multilingual support and backend admin CRUD.

## Features
- Responsive modern UI
- Languages: English, French, Arabic
- RTL support for Arabic
- Search input
- Accordion FAQ display
- Admin CRUD interface to manage questions/answers
- Easy integration into an existing CodeIgniter 4 app

## Installation

1. Copy the package files into your CodeIgniter 4 project.
2. Run the migration:
   ```bash
   php spark migrate
   ```
3. Visit:
   - Frontend: `/faq?lang=en`
   - Admin: `/admin/faqs`

## Database migration

```bash
php spark migrate
```

## Main files
- `app/Controllers/FaqController.php`
- `app/Controllers/Admin/FaqAdminController.php`
- `app/Models/FaqModel.php`
- `app/Database/Migrations/2026_10_22_000001_CreateFaqs.php`
- `app/Views/faq/index.php`
- `app/Views/admin/faq/index.php`
- `app/Views/admin/faq/form.php`
- `public/assets/css/faq.css`
- `public/assets/js/faq.js`

## Example SQL seed

```sql
INSERT INTO `faqs` (`locale`, `question`, `answer`, `sort_order`, `is_active`, `created_at`, `updated_at`) VALUES
('en', 'How can I contact support?', 'You can contact our support team through the contact form, email, or live chat.', 1, 1, NOW(), NOW()),
('fr', 'Comment puis-je contacter le support ?', 'Vous pouvez contacter notre équipe de support via le formulaire de contact, par e-mail ou via le chat en direct.', 1, 1, NOW(), NOW()),
('ar', 'كيف يمكنني التواصل مع الدعم؟', 'يمكنك التواصل مع فريق الدعم عبر نموذج الاتصال أو البريد الإلكتروني أو الدردشة المباشرة.', 1, 1, NOW(), NOW());
```

## Download archive

Use the GitHub Download ZIP button on this repository to download the package as a zip archive.
