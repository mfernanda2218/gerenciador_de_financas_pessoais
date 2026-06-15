let gastosCategoriaChart = null;
let receitaDespesaChart = null;
let evolucaoMensalChart = null;

function formatMoney(value) {
    const numberValue = Number(value || 0);
    return numberValue.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
}

function updateExportLink(month, year) {
    const exportLink = document.getElementById('exportCsvLink');
    if (!exportLink) return;
    const params = new URLSearchParams();
    if (month) params.set('month', month);
    if (year) params.set('year', year);
    const qs = params.toString();
    exportLink.href = qs ? `/export_csv?${qs}` : '/export_csv';
}

function setAlert(message) {
    const el = document.getElementById('alerta');
    if (!el) return;
    if (message) {
        el.textContent = message;
        el.style.display = 'block';
    } else {
        el.textContent = '';
        el.style.display = 'none';
    }
}

function loadDashboard() {
    const month = (document.getElementById('month')?.value || '').trim();
    const year = (document.getElementById('year')?.value || '').trim();

    updateExportLink(month, year);

    const params = new URLSearchParams();
    if (month) params.set('month', month);
    if (year) params.set('year', year);

    // Show loading state
    const statsElements = document.querySelectorAll('.stat .value');
    statsElements.forEach(el => el.textContent = 'Carregando...');

    fetch(`/dashboard_data?${params.toString()}`)
        .then(async (response) => {
            const data = await response.json();
            if (!response.ok) {
                throw new Error(data.message || 'Falha ao carregar o dashboard');
            }
            return data;
        })
        .then(data => {
            const totalMensalEl = document.getElementById('totalMensal');
            const receitaEl = document.getElementById('totalReceita');
            const despesaEl = document.getElementById('totalDespesa');

            if (totalMensalEl) totalMensalEl.textContent = formatMoney(data.total_mensal);
            if (receitaEl) receitaEl.textContent = formatMoney(data.total_receita);
            if (despesaEl) despesaEl.textContent = formatMoney(data.total_despesa);

            const monthlyLimitEl = document.getElementById('monthlyLimit');
            if (monthlyLimitEl && (monthlyLimitEl.value === '' || monthlyLimitEl.value == null)) {
                monthlyLimitEl.value = data.monthly_limit ?? '';
            }

            setAlert(data.alerta || '');

            if (gastosCategoriaChart) gastosCategoriaChart.destroy();
            if (receitaDespesaChart) receitaDespesaChart.destroy();
            if (evolucaoMensalChart) evolucaoMensalChart.destroy();

            const gastosCtx = document.getElementById('gastosCategoria');
            gastosCategoriaChart = new Chart(gastosCtx, {
                type: 'bar',
                data: {
                    labels: Object.keys(data.gastos_por_categoria || {}),
                    datasets: [{ label: 'Gastos', data: Object.values(data.gastos_por_categoria || {}), backgroundColor: 'rgba(255, 99, 132, 0.2)' }]
                },
                options: { responsive: true, maintainAspectRatio: false, scales: { y: { beginAtZero: true } } }
            });

            const receitaCtx = document.getElementById('receitaDespesa');
            receitaDespesaChart = new Chart(receitaCtx, {
                type: 'pie',
                data: {
                    labels: ['Receita', 'Despesa'],
                    datasets: [{ data: [data.receita_despesa?.receita || 0, data.receita_despesa?.despesa || 0], backgroundColor: ['#36a2eb', '#ff6384'] }]
                },
                options: { responsive: true, maintainAspectRatio: false }
            });

            const evolucaoCtx = document.getElementById('evolucaoMensal');
            evolucaoMensalChart = new Chart(evolucaoCtx, {
                type: 'line',
                data: {
                    labels: Object.keys(data.evolucao_mensal || {}),
                    datasets: [{ label: 'Saldo', data: Object.values(data.evolucao_mensal || {}), borderColor: '#4bc0c0' }]
                },
                options: { responsive: true, maintainAspectRatio: false, scales: { y: { beginAtZero: true } } }
            });
        })
        .catch(err => {
            setAlert(err.message || 'Erro ao carregar dados');
            const statsElements = document.querySelectorAll('.stat .value');
            statsElements.forEach(el => el.textContent = 'Erro');
        });
}

function addCategory() {
    const input = document.getElementById('category-name');
    const name = (input?.value || '').trim();
    if (!name) return;

    const button = document.querySelector('button[onclick="addCategory()"]');
    if (button) {
        button.disabled = true;
        button.textContent = 'Adicionando...';
    }

    fetch('/add_category', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: `name=${encodeURIComponent(name)}`
    })
        .then(async (response) => {
            const data = await response.json();
            if (!response.ok) {
                throw new Error(data.message || 'Falha ao adicionar categoria');
            }
            return data;
        })
        .then(() => {
            if (input) input.value = '';
            setAlert('Categoria adicionada com sucesso');
            setTimeout(() => setAlert(''), 2000);
        })
        .catch(err => {
            setAlert(err.message || 'Erro ao adicionar categoria');
        })
        .finally(() => {
            if (button) {
                button.disabled = false;
                button.textContent = 'Adicionar';
            }
        });
}

function saveMonthlyLimit() {
    const input = document.getElementById('monthlyLimit');
    const value = (input?.value || '').trim();

    const button = document.querySelector('button[onclick="saveMonthlyLimit()"]');
    if (button) {
        button.disabled = true;
        button.textContent = 'Salvando...';
    }

    fetch('/set_monthly_limit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: `monthly_limit=${encodeURIComponent(value)}`
    })
        .then(async (response) => {
            const data = await response.json();
            if (!response.ok) {
                throw new Error(data.message || 'Falha ao salvar limite');
            }
            return data;
        })
        .then((data) => {
            if (input) input.value = data.monthly_limit;
            setAlert('Limite salvo com sucesso');
            setTimeout(() => setAlert(''), 2000);
            loadDashboard();
        })
        .catch(err => {
            setAlert(err.message || 'Erro ao salvar limite');
        })
        .finally(() => {
            if (button) {
                button.disabled = false;
                button.textContent = 'Salvar limite';
            }
        });
}