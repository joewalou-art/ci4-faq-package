<?php

namespace App\Controllers;

use App\Models\FaqModel;

class FaqController extends BaseController
{
    protected $faqModel;

    public function __construct()
    {
        $this->faqModel = new FaqModel();
    }

    public function index(): string
    {
        $locale = $this->request->getGet('lang') ?? service('request')->getLocale() ?? 'en';
        $allowed = ['en', 'fr', 'ar'];

        if (! in_array($locale, $allowed, true)) {
            $locale = 'en';
        }

        $search = trim((string) ($this->request->getGet('q') ?? ''));
        $faqs = $this->faqModel->getActiveFaqs($locale, $search);

        $trans = [
            'en' => [
                'title' => 'Frequently Asked Questions',
                'subtitle' => 'Find quick answers to common questions.',
                'search_placeholder' => 'Search FAQs...',
                'language' => 'Language',
                'empty' => 'No results found for your search.',
            ],
            'fr' => [
                'title' => 'Questions Fréquemment Posées',
                'subtitle' => 'Trouvez rapidement des réponses aux questions courantes.',
                'search_placeholder' => 'Rechercher dans la FAQ...',
                'language' => 'Langue',
                'empty' => 'Aucun résultat trouvé pour votre recherche.',
            ],
            'ar' => [
                'title' => 'الأسئلة الشائعة',
                'subtitle' => 'اعثر على إجابات سريعة للأسئلة الشائعة.',
                'search_placeholder' => 'ابحث في الأسئلة الشائعة...',
                'language' => 'اللغة',
                'empty' => 'لم يتم العثور على نتائج.',
            ],
        ];

        $data = [
            'locale' => $locale,
            'faqs' => $faqs,
            'trans' => $trans[$locale],
            'lang_options' => [
                'en' => 'English',
                'fr' => 'Français',
                'ar' => 'العربية',
            ],
        ];

        return view('faq/index', $data);
    }
}
