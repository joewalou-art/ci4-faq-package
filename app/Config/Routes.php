<?php

namespace App\Config;

use CodeIgniter\Config\Routes as BaseRoutes;

// Create a new instance of route collection.
$routes = Services::routes();

// Frontend FAQ
$routes->get('faq', 'FaqController::index');

// Backend FAQ CRUD
$routes->group('admin', static function ($routes) {
    $routes->get('faqs', 'Admin\FaqAdminController::index');
    $routes->get('faqs/new', 'Admin\FaqAdminController::create');
    $routes->post('faqs', 'Admin\FaqAdminController::store');
    $routes->get('faqs/(:num)/edit', 'Admin\FaqAdminController::edit/$1');
    $routes->post('faqs/update/(:num)', 'Admin\FaqAdminController::update/$1');
    $routes->post('faqs/delete/(:num)', 'Admin\FaqAdminController::delete/$1');
});
