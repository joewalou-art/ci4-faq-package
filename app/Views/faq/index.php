<!DOCTYPE html>
<html lang="<?= esc($locale) ?>" dir="<?= ($locale === 'ar') ? 'rtl' : 'ltr' ?>">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title><?= esc($trans['title']) ?></title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;500;700;800&family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="<?= base_url('assets/css/faq.css') ?>">
</head>
<body class="<?= ($locale === 'ar') ? 'rtl-theme' : 'ltr-theme' ?>">
    <div class="faq-page">
        <div class="faq-shell">
            <header class="faq-header">
                <div class="faq-badge"><?= esc($trans['language']) ?> • <?= esc(strtoupper($locale)) ?></div>
                <h1><?= esc($trans['title']) ?></h1>
                <p><?= esc($trans['subtitle']) ?></p>

                <div class="faq-toolbar">
                    <div class="faq-search">
                        <span class="icon">⌕</span>
                        <input type="search" id="faqSearch" placeholder="<?= esc($trans['search_placeholder']) ?>" value="<?= esc($this->request->getGet('q') ?? '') ?>">
                    </div>

                    <div class="faq-language-switcher" aria-label="Language switcher">
                        <?php foreach ($lang_options as $key => $label): ?>
                            <?php
                                $url = site_url('faq') . '?lang=' . $key;
                                if ($this->request->getGet('q')) {
                                    $url .= '&q=' . urlencode((string) $this->request->getGet('q'));
                                }
                            ?>
                            <a href="<?= esc($url) ?>" class="<?= ($key === $locale) ? 'active' : '' ?>"><?= esc($label) ?></a>
                        <?php endforeach; ?>
                    </div>
                </div>
            </header>

            <main class="faq-list">
                <?php if (empty($faqs)): ?>
                    <div class="faq-empty"><?= esc($trans['empty']) ?></div>
                <?php else: ?>
                    <?php foreach ($faqs as $faq): ?>
                        <article class="faq-item">
                            <button class="faq-question" type="button" aria-expanded="false">
                                <span><?= esc($faq['question']) ?></span>
                                <span class="faq-icon">+</span>
                            </button>
                            <div class="faq-answer">
                                <div><?= esc($faq['answer']) ?></div>
                            </div>
                        </article>
                    <?php endforeach; ?>
                <?php endif; ?>
            </main>
        </div>
    </div>

    <script src="<?= base_url('assets/js/faq.js') ?>"></script>
</body>
</html>
