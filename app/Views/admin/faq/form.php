<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title><?= esc($title) ?></title>
    <link rel="stylesheet" href="<?= base_url('assets/css/faq.css') ?>">
</head>
<body class="admin-body">
    <div class="admin-wrap small">
        <div class="admin-header">
            <div>
                <h1><?= esc($title) ?></h1>
            </div>
            <a href="<?= site_url('admin/faqs') ?>" class="btn btn-secondary">Back</a>
        </div>

        <?php if (session()->getFlashdata('errors')): ?>
            <div class="alert error">
                <ul>
                    <?php foreach (session()->getFlashdata('errors') as $error): ?>
                        <li><?= esc($error) ?></li>
                    <?php endforeach; ?>
                </ul>
            </div>
        <?php endif; ?>

        <?php $action = isset($faq['id']) && $faq['id'] ? 'admin/faqs/update/' . $faq['id'] : 'admin/faqs'; ?>
        <form action="<?= site_url($action) ?>" method="post" class="admin-form">
            <?= csrf_field() ?>

            <div class="form-grid">
                <div class="field">
                    <label for="locale">Language</label>
                    <select id="locale" name="locale">
                        <option value="en" <?= ($faq['locale'] ?? 'en') === 'en' ? 'selected' : '' ?>>English</option>
                        <option value="fr" <?= ($faq['locale'] ?? 'en') === 'fr' ? 'selected' : '' ?>>Français</option>
                        <option value="ar" <?= ($faq['locale'] ?? 'en') === 'ar' ? 'selected' : '' ?>>العربية</option>
                    </select>
                </div>

                <div class="field">
                    <label for="sort_order">Order</label>
                    <input type="number" id="sort_order" name="sort_order" value="<?= esc($faq['sort_order'] ?? 0) ?>" min="0">
                </div>

                <div class="field field-full">
                    <label for="question">Question</label>
                    <input type="text" id="question" name="question" value="<?= esc($faq['question'] ?? '') ?>" required>
                </div>

                <div class="field field-full">
                    <label for="answer">Answer</label>
                    <textarea id="answer" name="answer" rows="8" required><?= esc($faq['answer'] ?? '') ?></textarea>
                </div>

                <div class="field">
                    <label for="is_active">Status</label>
                    <select id="is_active" name="is_active">
                        <option value="1" <?= (($faq['is_active'] ?? 1) == 1) ? 'selected' : '' ?>>Active</option>
                        <option value="0" <?= (($faq['is_active'] ?? 1) == 0) ? 'selected' : '' ?>>Inactive</option>
                    </select>
                </div>
            </div>

            <div class="form-actions">
                <button type="submit" class="btn btn-primary"><?= isset($faq['id']) && $faq['id'] ? 'Update FAQ' : 'Create FAQ' ?></button>
            </div>
        </form>
    </div>
</body>
</html>
