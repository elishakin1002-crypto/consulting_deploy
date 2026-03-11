// 登录页面JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // 获取DOM元素
    const loginForm = document.getElementById('login-form');
    const registerForm = document.getElementById('register-form');
    const tabBtns = document.querySelectorAll('.tab-btn');
    const loginMessage = document.getElementById('login-message');
    const registerMessage = document.getElementById('register-message');

    // 切换登录/注册表单
    if (tabBtns.length > 0) {
        tabBtns.forEach(btn => {
            btn.addEventListener('click', function() {
                // 移除所有活动状态
                tabBtns.forEach(b => b.classList.remove('active'));
                document.querySelectorAll('.tab-content').forEach(content => {
                    content.classList.remove('active');
                });

                // 添加活动状态到当前按钮和对应内容
                this.classList.add('active');
                const tabId = this.getAttribute('data-tab');
                document.getElementById(`${tabId}-form`).classList.add('active');

                // 清除消息
                if (loginMessage) loginMessage.textContent = '';
                if (registerMessage) registerMessage.textContent = '';
                if (loginMessage) loginMessage.className = 'login-message';
                if (registerMessage) registerMessage.className = 'login-message';
            });
        });
    }

    // 登录表单提交
    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // 获取表单数据
            const email = document.getElementById('login-email').value;
            const password = document.getElementById('login-password').value;
            const remember = document.getElementById('remember').checked;

            // 简单验证
            if (!email || !password) {
                showMessage(loginMessage, '请填写所有必填字段', 'error');
                return;
            }

            // 模拟登录请求
            simulateLoginRequest(email, password, remember);
        });
    }

    // 注册表单提交
    if (registerForm) {
        registerForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // 获取表单数据
            const name = document.getElementById('register-name').value;
            const email = document.getElementById('register-email').value;
            const password = document.getElementById('register-password').value;
            const confirmPassword = document.getElementById('register-confirm-password').value;
            const terms = document.getElementById('terms').checked;

            // 简单验证
            if (!name || !email || !password || !confirmPassword) {
                showMessage(registerMessage, '请填写所有必填字段', 'error');
                return;
            }

            if (password !== confirmPassword) {
                showMessage(registerMessage, '两次输入的密码不一致', 'error');
                return;
            }

            if (!terms) {
                showMessage(registerMessage, '请同意服务条款和隐私政策', 'error');
                return;
            }

            // 模拟注册请求
            simulateRegisterRequest(name, email, password);
        });
    }

    // 显示消息函数
    function showMessage(element, message, type) {
        if (!element) return;
        
        element.textContent = message;
        element.className = 'login-message';
        element.classList.add(type);
    }

    // 模拟登录请求
    function simulateLoginRequest(email, password, remember) {
        // 在实际应用中，这里应该是一个AJAX请求到服务器
        // 这里仅作演示，模拟登录成功
        
        // 显示加载状态
        showMessage(loginMessage, '登录中...', 'info');
        
        // 模拟网络延迟
        setTimeout(() => {
            // 模拟登录成功
            if (email === 'admin@example.com' && password === 'password') {
                showMessage(loginMessage, '登录成功！正在跳转...', 'success');
                
                // 如果选择了记住我，可以设置cookie或localStorage
                if (remember) {
                    localStorage.setItem('user_email', email);
                }
                
                // 模拟跳转到用户中心
                setTimeout(() => {
                    window.location.href = 'index.html';
                }, 1500);
            } else {
                // 模拟登录失败
                showMessage(loginMessage, '邮箱或密码错误，请重试', 'error');
            }
        }, 1500);
    }

    // 模拟注册请求
    function simulateRegisterRequest(name, email, password) {
        // 在实际应用中，这里应该是一个AJAX请求到服务器
        // 这里仅作演示，模拟注册成功
        
        // 显示加载状态
        showMessage(registerMessage, '注册中...', 'info');
        
        // 模拟网络延迟
        setTimeout(() => {
            // 模拟注册成功
            showMessage(registerMessage, '注册成功！请登录您的账户', 'success');
            
            // 清空表单
            document.getElementById('register-name').value = '';
            document.getElementById('register-email').value = '';
            document.getElementById('register-password').value = '';
            document.getElementById('register-confirm-password').value = '';
            document.getElementById('terms').checked = false;
            
            // 延迟后切换到登录表单
            setTimeout(() => {
                document.querySelector('[data-tab="login"]').click();
            }, 2000);
        }, 1500);
    }

    // 自动填充记住的邮箱
    const savedEmail = localStorage.getItem('user_email');
    if (savedEmail && document.getElementById('login-email')) {
        document.getElementById('login-email').value = savedEmail;
        document.getElementById('remember').checked = true;
    }

    // 第三方/快捷登录入口提示
    document.querySelectorAll('.social-btn').forEach((btn) => {
        btn.addEventListener('click', function() {
            if (this.classList.contains('wechat')) {
                showMessage(loginMessage, '微信登录功能开发中，请先使用邮箱密码登录。', 'info');
                return;
            }
            if (this.classList.contains('phone')) {
                showMessage(loginMessage, '手机号快捷登录功能开发中，请先使用邮箱密码登录。', 'info');
            }
        });
    });
});
