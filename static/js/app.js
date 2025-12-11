document.addEventListener('DOMContentLoaded', () => {
    const API_BASE_URL = "http://127.0.0.1:8099";

    const views = {
        dashboard: document.getElementById('dashboard-view'),
        products: document.getElementById('products-view'),
        customers: document.getElementById('customers-view'),
        graphql: document.getElementById('graphql-view'),
        admin: document.getElementById('admin-view'),
    };

    const navLinks = document.querySelectorAll('.sidebar .nav-link');

    // --- Generic Fetch Function ---
    async function fetchData(endpoint, options = {}) {
        try {
            // A helper to add a loading spinner for write operations
            document.body.style.cursor = 'wait';

            const response = await fetch(`${API_BASE_URL}${endpoint}`, options);
            
            // For 204 No Content, response.json() will fail, so we handle it early
            if (response.status === 204) {
                return true;
            }

            const responseData = await response.json();
            if (!response.ok) {
                throw new Error(responseData.detail || `HTTP error! status: ${response.status}`);
            }
            return responseData;
        } catch (error) {
            console.error('Fetch error:', error);
            alert(`Error: ${error.message}`);
            return null;
        } finally {
            document.body.style.cursor = 'default';
        }
    }

    // --- View Navigation ---
    function showView(viewId) {
        navLinks.forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('data-view') === viewId) {
                link.classList.add('active');
            }
        });

        for (const id in views) {
            views[id].classList.toggle('active', id === viewId);
        }
        window.location.hash = viewId;
    }

    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const viewId = link.getAttribute('data-view');
            showView(viewId);
            loadViewData(viewId);
        });
    });

    // --- Data Loading and Rendering ---
    function loadViewData(viewId) {
        switch (viewId) {
            case 'dashboard':
                loadDashboardData();
                break;
            case 'products':
                loadProductsData();
                break;
            case 'customers':
                loadCustomersData();
                break;
            case 'admin':
                loadAdminData();
                break;
        }
    }

    async function loadDashboardData() {
        const resultDiv = document.getElementById('productOfTheDayResult');
        resultDiv.innerHTML = '<div class="text-center"><div class="spinner-border" role="status"></div></div>';
        const data = await fetchData('/product-of-the-day-details');
        if (data) {
            renderProductOfTheDay(data, resultDiv);
        } else {
            resultDiv.innerHTML = '<div class="alert alert-warning">Could not load product of the day.</div>';
        }
    }

    async function loadProductsData() {
        const tableBody = document.getElementById('productsTableBody');
        tableBody.innerHTML = '<tr><td colspan="4" class="text-center"><div class="spinner-border" role="status"></div></td></tr>';
        const products = await fetchData('/products');
        tableBody.innerHTML = '';
        if (products && products.length > 0) {
            products.forEach(p => {
                tableBody.innerHTML += `<tr><td>${p.id}</td><td>${p.flavor}</td><td>${p.kind}</td><td>$${p.price.toFixed(2)}</td></tr>`;
            });
        } else {
            tableBody.innerHTML = '<tr><td colspan="4" class="text-center">No products found.</td></tr>';
        }
    }

    async function loadCustomersData() {
        const tableBody = document.getElementById('customersTableBody');
        tableBody.innerHTML = '<tr><td colspan="3" class="text-center"><div class="spinner-border" role="status"></div></td></tr>';
        const customers = await fetchData('/customers');
        tableBody.innerHTML = '';
        if (customers && customers.length > 0) {
            customers.forEach(c => {
                tableBody.innerHTML += `<tr><td>${c.id}</td><td>${c.firstName}</td><td>${c.lastName}</td></tr>`;
            });
        } else {
            tableBody.innerHTML = '<tr><td colspan="3" class="text-center">No customers found.</td></tr>';
        }
    }

    async function loadAdminData() {
        // Load current daily deal
        const currentDealDiv = document.getElementById('current-deal-display');
        currentDealDiv.innerHTML = '<div class="spinner-border spinner-border-sm" role="status"></div>';
        const deal = await fetchData('/products/daily-deal');
        renderCurrentDeal(deal, currentDealDiv);

        // Populate product dropdown
        const productSelect = document.getElementById('deal-product-select');
        productSelect.innerHTML = '';
        const products = await fetchData('/products');
        if (products) {
            products.forEach(p => {
                productSelect.innerHTML += `<option value="${p.id}">${p.flavor} ${p.kind}</option>`;
            });
        }
    }

    function renderProductOfTheDay(data, container) {
        const deal = data.deal_details;
        const reviews = data.reviews ? data.reviews.reviews : [];
        let reviewsHtml = '<h6>No reviews yet.</h6>';
        if (reviews.length > 0) {
            reviewsHtml = reviews.map(r => `
                <div class="review">
                    <p class="mb-1"><strong>Rating: ${r.rating}/5</strong> - "${r.comment}"</p>
                    <small class="text-muted">By Customer #${r.customer_id} on ${new Date(r.timestamp).toLocaleDateString()}</small>
                </div>
            `).join('');
        }
        container.innerHTML = `
            <div class="card-body">
                <h5 class="card-title">${deal.message}</h5>
                <p class="card-text"><b>${deal.product.flavor} ${deal.product.kind}</b></p>
                <p class="card-text">
                    Original Price: <del>$${deal.product.price.toFixed(2)}</del><br>
                    <strong>Discounted Price: $${deal.discounted_price.toFixed(2)}</strong>
                </p>
            </div>
            <div class="card mt-3"><div class="card-header">User Reviews</div><div class="card-body">${reviewsHtml}</div></div>`;
    }

    function renderCurrentDeal(deal, container) {
        if (deal) {
            container.innerHTML = `
                <div class="alert alert-info">
                    <p class="mb-1"><strong>Current Deal:</strong> ${deal.message}</p>
                    <p class="mb-1">Product: ${deal.product.flavor} ${deal.product.kind}</p>
                    <button id="delete-deal-btn" class="btn btn-sm btn-danger mt-2">Delete Deal</button>
                </div>`;
            document.getElementById('delete-deal-btn').addEventListener('click', handleDeleteDeal);
        } else {
            container.innerHTML = '<div class="alert alert-secondary">No daily deal is currently set.</div>';
        }
    }

    // --- Event Listeners & Handlers ---

    // Parameterized queries
    document.getElementById('fetchCustomerByIdBtn').addEventListener('click', async () => {
        const customerId = document.getElementById('customerIdInput').value;
        const resultDiv = document.getElementById('singleCustomerResult');
        if (!customerId) return alert('Please enter a customer ID.');
        resultDiv.innerHTML = '<div class="spinner-border spinner-border-sm" role="status"></div>';
        const customer = await fetchData(`/customers/${customerId}`);
        if (customer) {
            resultDiv.innerHTML = `<div class="card bg-light"><div class="card-body"><h5 class="card-title">${customer.firstName} ${customer.lastName}</h5><p class="card-text">ID: ${customer.id}</p></div></div>`;
        } else {
            resultDiv.innerHTML = '<div class="alert alert-warning">Customer not found.</div>';
        }
    });

    document.getElementById('fetchProductReviewsBtn').addEventListener('click', async function() {
        const productId = document.getElementById('productIdInput').value;
        const resultDiv = document.getElementById('productReviewsResult');
        if (!productId) return alert('Please enter a product ID.');
        resultDiv.innerHTML = '<div class="spinner-border spinner-border-sm" role="status"></div>';
        const data = await fetchData(`/products/${productId}/reviews`);
        if (data) {
            const reviews = data.reviews || [];
            let reviewsHtml = '<h6>No reviews yet for this product.</h6>';
            if (reviews.length > 0) {
                reviewsHtml = reviews.map(r => `
                    <div class="review">
                        <p class="mb-1"><strong>Rating: ${r.rating}/5</strong> - "${r.comment}"</p>
                        <small class="text-muted">By Customer #${r.customer_id} on ${new Date(r.timestamp).toLocaleDateString()}</small>
                        <button class="btn btn-sm btn-outline-danger float-end delete-review-btn" data-product-id="${productId}" data-review-id="${r.review_id}">Delete</button>
                    </div>
                `).join('');
            }
            resultDiv.innerHTML = `<div class="card bg-light"><div class="card-header">Reviews for Product ID: ${data.product_id}</div><div class="card-body">${reviewsHtml}</div></div>`;
        } else {
            resultDiv.innerHTML = '<div class="alert alert-warning">No reviews found for this product.</div>';
        }
    });

    // GraphQL Explorer
    const gqlQueryInput = document.getElementById('graphql-query');
    gqlQueryInput.value = `query GetProductsAndDeal {
    products { id flavor price }
    dailyDeal { message product { flavor } }
}`;
    document.getElementById('execute-graphql').addEventListener('click', async () => {
        const responseDiv = document.getElementById('graphql-response');
        if (!gqlQueryInput.value.trim()) return responseDiv.textContent = 'Please enter a query.';
        responseDiv.textContent = 'Loading...';
        const response = await fetchData('/graphql', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query: gqlQueryInput.value })
        });
        responseDiv.textContent = response ? JSON.stringify(response, null, 2) : 'An error occurred.';
    });

    // Admin Forms
    document.getElementById('set-deal-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const productId = document.getElementById('deal-product-select').value;
        const discount = document.getElementById('deal-discount-input').value;
        const newDeal = await fetchData('/products/daily-deal', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ product_id: productId, discount_percent: parseInt(discount) })
        });
        if (newDeal) {
            alert('Daily deal has been set!');
            loadAdminData();
        }
    });

    document.getElementById('add-review-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const form = e.target;
        const review = {
            product_id: form.querySelector('#review-product-id').value,
            customer_id: parseInt(form.querySelector('#review-customer-id').value),
            rating: parseInt(form.querySelector('#review-rating').value),
            comment: form.querySelector('#review-comment').value,
            tags: form.querySelector('#review-tags').value.split(',').map(tag => tag.trim()),
        };
        const newReview = await fetchData(`/products/${review.product_id}/reviews`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(review)
        });
        if (newReview) {
            alert('Review added successfully!');
            form.reset();
        }
    });
    
    // Event delegation for delete buttons
    document.body.addEventListener('click', async function(e) {
        if (e.target && e.target.matches('button.delete-review-btn')) {
            const btn = e.target;
            const productId = btn.getAttribute('data-product-id');
            const reviewId = btn.getAttribute('data-review-id');
            if (confirm(`Are you sure you want to delete this review?`)) {
                const success = await fetchData(`/products/${productId}/reviews/${reviewId}`, { method: 'DELETE' });
                if (success) {
                    alert('Review deleted.');
                    btn.closest('.review').remove();
                }
            }
        }
    });

    async function handleDeleteDeal() {
        if (confirm('Are you sure you want to delete the current daily deal?')) {
            const success = await fetchData('/products/daily-deal', { method: 'DELETE' });
            if (success) {
                alert('Daily deal deleted.');
                loadAdminData();
            }
        }
    }

    // --- Initial Load ---
    const initialView = window.location.hash.replace('#', '') || 'dashboard';
    showView(initialView);
    loadViewData(initialView);
});

