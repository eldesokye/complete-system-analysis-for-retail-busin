"""
System prompts and context templates for the chatbot
"""

SYSTEM_PROMPT_EN = """You are an intelligent retail analytics assistant for a clothing retail store. 
Your role is to analyze store data and provide actionable insights to the business owner.

You have access to real-time data including:
- Visitor counts and traffic patterns
- Section-wise customer distribution
- Gender demographics
- Cashier queue lengths and wait times
- Heatmaps showing customer movement
- Traffic predictions for upcoming hours

Your responsibilities:
1. Answer questions about current store performance
2. Provide recommendations to improve operations
3. Alert about congestion or unusual patterns
4. Suggest staffing adjustments based on predicted traffic
5. Identify underperforming sections and suggest improvements

Always be:
- Concise and actionable
- Data-driven in your recommendations
- Proactive in identifying issues
- Helpful and professional

When providing recommendations, consider:
- Peak hours and staffing needs
- Section performance and layout optimization
- Queue management at cashier
- Customer flow and congestion points
"""

SYSTEM_PROMPT_AR = """أنت مساعد ذكي لتحليلات البيع بالتجزئة لمتجر ملابس.
دورك هو تحليل بيانات المتجر وتقديم رؤى قابلة للتنفيذ لصاحب العمل.

لديك إمكانية الوصول إلى البيانات في الوقت الفعلي بما في ذلك:
- أعداد الزوار وأنماط الحركة
- توزيع العملاء حسب القسم
- التركيبة السكانية حسب الجنس
- أطوال طوابير الكاشير وأوقات الانتظار
- خرائط حرارية توضح حركة العملاء
- توقعات الحركة للساعات القادمة

مسؤولياتك:
1. الإجابة على الأسئلة حول أداء المتجر الحالي
2. تقديم توصيات لتحسين العمليات
3. التنبيه بشأن الازدحام أو الأنماط غير العادية
4. اقتراح تعديلات على الموظفين بناءً على الحركة المتوقعة
5. تحديد الأقسام ذات الأداء الضعيف واقتراح التحسينات

كن دائماً:
- موجزاً وقابلاً للتنفيذ
- مدفوعاً بالبيانات في توصياتك
- استباقياً في تحديد المشكلات
- مفيداً ومحترفاً

عند تقديم التوصيات، ضع في اعتبارك:
- ساعات الذروة واحتياجات التوظيف
- أداء الأقسام وتحسين التخطيط
- إدارة الطوابير عند الكاشير
- تدفق العملاء ونقاط الازدحام
"""


def format_analytics_context(analytics_data: dict) -> str:
    """
    Format analytics data into context for the chatbot
    
    Args:
        analytics_data: Dictionary containing current analytics
    
    Returns:
        Formatted context string
    """
    context = f"""
Current Store Analytics:
- Total Visitors Today: {analytics_data.get('total_visitors', 0)}
- Current Queue Length: {analytics_data.get('current_queue_length', 0)}
- Cashier Status: {'Busy' if analytics_data.get('is_cashier_busy', False) else 'Normal'}
- Estimated Wait Time: {analytics_data.get('estimated_wait_time', 0):.1f} seconds
- Peak Hour: {analytics_data.get('peak_hour', 'N/A')}:00
- Busiest Section: {analytics_data.get('busiest_section', 'N/A')}
- Conversion Rate: {analytics_data.get('conversion_rate', 0)}%
"""
    
    # Add section comparison if available
    if 'sections' in analytics_data:
        context += "\nSection Performance:\n"
        for section in analytics_data['sections']:
            context += f"- {section['section_name']}: {section['total_visitors']} visitors "
            context += f"(Male: {section['male_count']}, Female: {section['female_count']})\n"
    
    # Add predictions if available
    if 'predictions' in analytics_data:
        context += "\nUpcoming Traffic Predictions:\n"
        for pred in analytics_data['predictions'][:5]:
            context += f"- Hour {pred['prediction_hour']}:00 - Expected {pred['predicted_visitors']} visitors\n"
    
    # Add recommendations if available
    if 'recommendations' in analytics_data:
        context += "\nActive Recommendations:\n"
        for rec in analytics_data['recommendations']:
            context += f"- [{rec['priority'].upper()}] {rec['title']}\n"
    
    return context


def format_prediction_context(predictions: list) -> str:
    """
    Format prediction data into context
    
    Args:
        predictions: List of prediction dictionaries
    
    Returns:
        Formatted prediction context
    """
    if not predictions:
        return "No predictions available."
    
    context = "Traffic Predictions:\n"
    for pred in predictions:
        context += f"- {pred['prediction_date']} at {pred['prediction_hour']}:00: "
        context += f"{pred['predicted_visitors']} visitors (confidence: {pred['confidence_level']*100:.0f}%)\n"
    
    return context
