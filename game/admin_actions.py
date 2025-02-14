from django.contrib import admin
from .models import Mission, Question

def create_trade_route_questions(modeladmin, request, queryset):
    """Bulk create questions for Trade Route mission"""
    # Get the Trade Route mission
    trade_mission = Mission.objects.get(mission_type='TRADE_ROUTE')
    
    questions = [
        {
            'scenario_title': 'Risk Assessment',
            'scenario': 'Scouts have reported potential bandit activity along the proposed trade route.',
            'text': 'How should you address this risk in your project plan?',
            'option_a': 'Hire armed guards to patrol the route',
            'option_b': 'Ignore the reports as they might be exaggerated',
            'option_c': 'Develop a comprehensive risk management plan including alternative routes and security measures',
            'option_d': 'Cancel the trade route project entirely',
            'correct_option': 'C',
            'explanation': 'A comprehensive risk management plan allows for multiple mitigation strategies and contingencies, making the project more resilient.',
            'consequence_a': 'Increased project costs without addressing all risk factors',
            'consequence_b': 'The project faces serious security threats without proper preparation',
            'consequence_c': 'The trade route operates safely with multiple backup plans',
            'consequence_d': 'Lost opportunity for economic growth and trade relationships'
        },
        {
            'scenario_title': 'Resource Allocation',
            'scenario': 'Multiple merchant guilds are requesting priority access to the trade route.',
            'text': 'What\'s the best approach to handle resource allocation?',
            'option_a': 'Give priority to the highest bidder only',
            'option_b': 'Create a fair scheduling system with clear allocation rules',
            'option_c': 'Let merchants fight it out among themselves',
            'option_d': 'Restrict access to only one merchant guild',
            'correct_option': 'B',
            'explanation': 'Fair resource allocation with clear rules ensures project sustainability and stakeholder satisfaction.',
            'consequence_a': 'Creates resentment and potential conflicts among merchants',
            'consequence_b': 'Establishes a sustainable and fair trading system',
            'consequence_c': 'Leads to chaos and potential violence',
            'consequence_d': 'Limits economic potential and creates monopoly'
        },
        {
            'scenario_title': 'Schedule Management',
            'scenario': 'Construction of the trade route is taking longer than planned due to terrain challenges.',
            'text': 'How should you adjust the project schedule?',
            'option_a': 'Force workers to work longer hours',
            'option_b': 'Ignore delays and maintain original timeline',
            'option_c': 'Evaluate the critical path and adjust resources accordingly',
            'option_d': 'Abandon the difficult sections of the route',
            'correct_option': 'C',
            'explanation': 'Analyzing the critical path helps identify where additional resources will have the most impact on the schedule.',
            'consequence_a': 'Worker fatigue leads to mistakes and safety issues',
            'consequence_b': 'Project quality suffers from rushed work',
            'consequence_c': 'Project completes efficiently with maintained quality',
            'consequence_d': 'Route becomes less valuable due to missing sections'
        },
        {
            'scenario_title': 'Stakeholder Communication',
            'scenario': 'Local villages along the route are concerned about increased traffic and noise.',
            'text': 'What communication strategy should you implement?',
            'option_a': 'Hold regular meetings with village leaders to address concerns',
            'option_b': 'Ignore village concerns as the trade route is more important',
            'option_c': 'Send a single written notice to all villages',
            'option_d': 'Redirect the route without consulting villages',
            'correct_option': 'A',
            'explanation': 'Regular stakeholder engagement helps address concerns proactively and builds support for the project.',
            'consequence_a': 'Villages become project supporters and help protect the route',
            'consequence_b': 'Local resistance creates ongoing problems',
            'consequence_c': 'Poor communication leads to misunderstandings',
            'consequence_d': 'Wastes resources and creates new problems'
        },
        {
            'scenario_title': 'Quality Control',
            'scenario': 'Contractors suggest using cheaper materials for road construction.',
            'text': 'How do you maintain quality standards?',
            'option_a': 'Accept cheaper materials to save money',
            'option_b': 'Implement quality control checkpoints and material testing',
            'option_c': 'Let contractors decide on materials',
            'option_d': 'Double the material budget without analysis',
            'correct_option': 'B',
            'explanation': 'Regular quality control ensures the trade route will be durable and safe for long-term use.',
            'consequence_a': 'Route requires frequent repairs and becomes unsafe',
            'consequence_b': 'Route remains reliable and maintenance costs stay low',
            'consequence_c': 'Inconsistent quality creates safety hazards',
            'consequence_d': 'Project costs spiral without guaranteed quality'
        }
    ]
    
    for q_data in questions:
        Question.objects.create(
            mission=trade_mission,
            **q_data
        )
create_trade_route_questions.short_description = "Create Trade Route Mission Questions"