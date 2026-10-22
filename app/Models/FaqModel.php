<?php

namespace App\Models;

use CodeIgniter\Model;

class FaqModel extends Model
{
    protected $table = 'faqs';
    protected $primaryKey = 'id';
    protected $useAutoIncrement = true;

    protected $returnType = 'array';
    protected $useSoftDeletes = false;

    protected $allowedFields = [
        'locale',
        'question',
        'answer',
        'sort_order',
        'is_active',
    ];

    protected $useTimestamps = true;
    protected $createdField = 'created_at';
    protected $updatedField = 'updated_at';
    protected $dateFormat = 'datetime';

    public function getActiveFaqs(string $locale = 'en', ?string $search = null): array
    {
        $builder = $this->where('is_active', 1)
            ->where('locale', $locale)
            ->orderBy('sort_order', 'ASC');

        if (!empty($search)) {
            $builder->groupStart()
                ->like('question', $search)
                ->orLike('answer', $search)
                ->groupEnd();
        }

        return $builder->findAll();
    }

    public function getOrderedFaqs(): array
    {
        return $this->orderBy('locale', 'ASC')
            ->orderBy('sort_order', 'ASC')
            ->findAll();
    }
}
