<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FAQ Admin</title>
    <link rel="stylesheet" href="<?= base_url('assets/css/faq.css') ?>">
</head>
<body class="admin-body">
    <div class="admin-wrap">
        <div class="admin-header">
            <div>
                <h1>FAQ Management</h1>
                <p>Manage multilingual FAQ entries</p>
            </div>
            <a href="<?= site_url('admin/faqs/new') ?>" class="btn btn-primary">Add FAQ</a>
        </div>

        <?php if (session()->getFlashdata('success')): ?>
            <div class="alert success"><?= esc(session()->getFlashdata('success')) ?></div>
        <?php endif; ?>

        <div class="admin-card">
            <table class="faq-table">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Locale</th>
                        <th>Question</th>
                        <th>Answer</th>
                        <th>Order</th>
                        <th>Status</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    <?php if (empty($faqs)): ?>
                        <tr>
                            <td colspan="7" class="empty-cell">No FAQs found.</td>
                        </tr>
                    <?php else: ?>
                        <?php foreach ($faqs as $faq): ?>
                            <tr>
                                <td><?= esc($faq['id']) ?></td>
                                <td><?= esc(strtoupper($faq['locale'])) ?></td>
                                <td><?= esc($faq['question']) ?></td>
                                <td><?= esc(substr($faq['answer'], 0, 90)) ?><?= (strlen($faq['answer']) > 90) ? '...' : '' ?></td>
                                <td><?= esc($faq['sort_order']) ?></td>
                                <td>
                                    <span class="status-badge <?= ($faq['is_active'] ? 'active' : 'inactive') ?>">
                                        <?= ($faq['is_active'] ? 'Active' : 'Inactive') ?>
                                    </span>
                                </td>
                                <td class="action-cell">
                                    <a href="<?= site_url('admin/faqs/' . $faq['id'] . '/edit') ?>" class="btn btn-small btn-secondary">Edit</a>
                                    <form action="<?= site_url('admin/faqs/delete/' . $faq['id']) ?>" method="post" onsubmit="return confirm('Delete this FAQ?');">
                                        <?= csrf_field() ?>
                                        <button type="submit" class="btn btn-small btn-danger">Delete</button>
                                    </form>
                                </td>
                            </tr>
                        <?php endforeach; ?>
                    <?php endif; ?>
                </tbody>
            </table>
        </div>
    </div>
</body>
</html>
