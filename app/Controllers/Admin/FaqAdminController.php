<?php

namespace App\Controllers\Admin;

use App\Controllers\BaseController;
use App\Models\FaqModel;
use CodeIgniter\HTTP\RedirectResponse;

class FaqAdminController extends BaseController
{
    protected $faqModel;

    public function __construct()
    {
        $this->faqModel = new FaqModel();
    }

    public function index(): string
    {
        $faqs = $this->faqModel->getOrderedFaqs();

        return view('admin/faq/index', [
            'faqs' => $faqs,
        ]);
    }

    public function create(): string
    {
        return view('admin/faq/form', [
            'faq' => [
                'id' => '',
                'locale' => 'en',
                'question' => '',
                'answer' => '',
                'sort_order' => 0,
                'is_active' => 1,
            ],
            'title' => 'Create FAQ',
        ]);
    }

    public function store(): RedirectResponse
    {
        $data = $this->request->getPost();

        $this->validation->setRules([
            'locale' => 'required|max_length[5]',
            'question' => 'required',
            'answer' => 'required',
            'sort_order' => 'required|integer',
            'is_active' => 'required|in_list[0,1]',
        ]);

        if (! $this->validation->withRequest($this->request)->run()) {
            return redirect()->back()->withInput()->with('errors', $this->validation->getErrors());
        }

        $this->faqModel->insert([
            'locale' => $data['locale'],
            'question' => trim($data['question']),
            'answer' => trim($data['answer']),
            'sort_order' => (int) $data['sort_order'],
            'is_active' => (int) $data['is_active'],
        ]);

        return redirect()->to('/admin/faqs')->with('success', 'FAQ created successfully.');
    }

    public function edit(int $id): string
    {
        $faq = $this->faqModel->find($id);

        if (! $faq) {
            throw \CodeIgniter\Exceptions\PageNotFoundException::forPageNotFound();
        }

        return view('admin/faq/form', [
            'faq' => $faq,
            'title' => 'Edit FAQ',
        ]);
    }

    public function update(int $id): RedirectResponse
    {
        $faq = $this->faqModel->find($id);

        if (! $faq) {
            throw \CodeIgniter\Exceptions\PageNotFoundException::forPageNotFound();
        }

        $data = $this->request->getPost();

        $this->validation->setRules([
            'locale' => 'required|max_length[5]',
            'question' => 'required',
            'answer' => 'required',
            'sort_order' => 'required|integer',
            'is_active' => 'required|in_list[0,1]',
        ]);

        if (! $this->validation->withRequest($this->request)->run()) {
            return redirect()->back()->withInput()->with('errors', $this->validation->getErrors());
        }

        $this->faqModel->update($id, [
            'locale' => $data['locale'],
            'question' => trim($data['question']),
            'answer' => trim($data['answer']),
            'sort_order' => (int) $data['sort_order'],
            'is_active' => (int) $data['is_active'],
        ]);

        return redirect()->to('/admin/faqs')->with('success', 'FAQ updated successfully.');
    }

    public function delete(int $id): RedirectResponse
    {
        $faq = $this->faqModel->find($id);

        if ($faq) {
            $this->faqModel->delete($id);
        }

        return redirect()->to('/admin/faqs')->with('success', 'FAQ deleted successfully.');
    }
}
