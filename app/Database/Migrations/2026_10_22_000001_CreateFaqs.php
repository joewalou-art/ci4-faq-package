<?php

namespace App\Database\Migrations;

use CodeIgniter\Database\Migration;

class CreateFaqs extends Migration
{
    public function up()
    {
        $this->forge->addField([
            'id' => [
                'type' => 'INT',
                'constraint' => 11,
                'unsigned' => true,
                'auto_increment' => true,
            ],
            'locale' => [
                'type' => 'VARCHAR',
                'constraint' => 5,
                'default' => 'en',
            ],
            'question' => [
                'type' => 'TEXT',
            ],
            'answer' => [
                'type' => 'TEXT',
            ],
            'sort_order' => [
                'type' => 'INT',
                'constraint' => 5,
                'default' => 0,
            ],
            'is_active' => [
                'type' => 'TINYINT',
                'constraint' => 1,
                'default' => 1,
            ],
            'created_at' => [
                'type' => 'DATETIME',
                'null' => true,
            ],
            'updated_at' => [
                'type' => 'DATETIME',
                'null' => true,
            ],
        ]);

        $this->forge->addKey('id', true);
        $this->forge->createTable('faqs');
    }

    public function down()
    {
        $this->forge->dropTable('faqs');
    }
}
