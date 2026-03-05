// 联系页面JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // 获取DOM元素
    const contactForm = document.getElementById('contactForm');
    const formMessage = document.getElementById('form-message');
    const faqItems = document.querySelectorAll('.faq-item');

    // 联系表单提交
    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // 获取表单数据
            const name = document.getElementById('name').value;
            const email = document.getElementById('email').value;
            const phone = document.getElementById('phone').value;
            const company = document.getElementById('company').value;
            const subject = document.getElementById('subject').value;
            const message = document.getElementById('message').value;

            // 简单验证
            if (!name || !email || !subject || !message) {
                showMessage('请填写所有必填字段', 'error');
                return;
            }

            // 验证邮箱格式
            if (!validateEmail(email)) {
                showMessage('请输入有效的电子邮箱地址', 'error');
                return;
            }

            // 模拟表单提交
            simulateFormSubmission(name, email, phone, company, subject, message);
        });
    }

    // FAQ 切换效果
    if (faqItems.length > 0) {
        faqItems.forEach(item => {
            const question = item.querySelector('.faq-question');
            question.addEventListener('click', () => {
                // 关闭其他打开的FAQ项
                faqItems.forEach(otherItem => {
                    if (otherItem !== item && otherItem.classList.contains('active')) {
                        otherItem.classList.remove('active');
                        const icon = otherItem.querySelector('.toggle-icon i');
                        icon.className = 'fas fa-plus';
                    }
                });

                // 切换当前FAQ项
                item.classList.toggle('active');
                const icon = item.querySelector('.toggle-icon i');
                if (item.classList.contains('active')) {
                    icon.className = 'fas fa-minus';
                } else {
                    icon.className = 'fas fa-plus';
                }
            });
        });
    }

    // 显示消息函数
    function showMessage(message, type) {
        if (!formMessage) return;
        
        formMessage.textContent = message;
        formMessage.className = 'form-message';
        formMessage.classList.add(type);
    }

    // 验证邮箱格式
    function validateEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    }

    // 模拟表单提交
    function simulateFormSubmission(name, email, phone, company, subject, message) {
        // 在实际应用中，这里应该是一个AJAX请求到服务器
        // 这里仅作演示，模拟提交成功
        
        // 显示加载状态
        showMessage('正在提交...', 'info');
        
        // 模拟网络延迟
        setTimeout(() => {
            // 模拟提交成功
            showMessage('消息已成功发送！我们会尽快回复您。', 'success');
            
            // 清空表单
            contactForm.reset();
            
            // 3秒后隐藏消息
            setTimeout(() => {
                formMessage.className = 'form-message';
            }, 3000);
        }, 1500);
    }
});