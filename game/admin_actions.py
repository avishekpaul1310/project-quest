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

def create_castle_restoration_questions(modeladmin, request, queryset):
    """Bulk create questions for Castle Restoration mission"""
    castle_mission = Mission.objects.get(mission_type='CASTLE_RESTORATION')
    
    questions = [
        {
            'scenario_title': 'Project Approach Selection',
            'scenario': 'The castle restoration involves both structural repairs and artistic renovations.',
            'text': 'Which project management approach should you use?',
            'option_a': 'Use only traditional waterfall for everything',
            'option_b': 'Apply agile methods to all aspects',
            'option_c': 'Tailor the approach: predictive for structural work, agile for artistic elements',
            'option_d': 'Let each team choose their own approach without coordination',
            'correct_option': 'C',
            'explanation': 'Different aspects of the project require different approaches. Structural work benefits from predictive planning, while artistic elements need flexibility.',
            'consequence_a': 'Artistic elements suffer from rigid planning',
            'consequence_b': 'Structural work becomes disorganized and unsafe',
            'consequence_c': 'Project proceeds efficiently with appropriate methods for each aspect',
            'consequence_d': 'Lack of coordination leads to chaos'
        },
        {
            'scenario_title': 'Cost Management',
            'scenario': 'Rare materials needed for restoration are more expensive than estimated.',
            'text': 'How do you handle this cost variance?',
            'option_a': 'Use cheaper substitute materials',
            'option_b': 'Analyze cost-benefit of materials and adjust budget with stakeholder approval',
            'option_c': 'Exceed budget without consultation',
            'option_d': 'Cancel the restoration of sections requiring expensive materials',
            'correct_option': 'B',
            'explanation': 'Cost variances require careful analysis and stakeholder consultation to maintain project value.',
            'consequence_a': 'Restoration quality is compromised',
            'consequence_b': 'Project maintains quality while managing costs effectively',
            'consequence_c': 'Project faces budget crisis',
            'consequence_d': 'Castle restoration becomes incomplete'
        },
        {
            'scenario_title': 'Quality Standards',
            'scenario': 'Historic preservation experts have specific requirements for restoration techniques.',
            'text': 'How do you ensure quality compliance?',
            'option_a': 'Implement regular quality inspections and documentation',
            'option_b': 'Rush the work to meet deadlines',
            'option_c': 'Ignore expert requirements to save time',
            'option_d': 'Leave quality control to individual workers',
            'correct_option': 'A',
            'explanation': 'Historic restoration requires strict quality control and documentation to preserve authenticity.',
            'consequence_a': 'Restoration meets historical standards and preservation goals',
            'consequence_b': 'Work fails to meet preservation standards',
            'consequence_c': 'Historical value is compromised',
            'consequence_d': 'Inconsistent quality damages castle\'s heritage'
        },
        {
            'scenario_title': 'Resource Allocation',
            'scenario': 'Multiple skilled artisans are needed simultaneously in different castle sections.',
            'text': 'How do you manage resource conflicts?',
            'option_a': 'First come, first served basis',
            'option_b': 'Create a resource calendar with prioritized scheduling',
            'option_c': 'Clone the artisans',
            'option_d': 'Skip areas requiring special skills',
            'correct_option': 'B',
            'explanation': 'Resource leveling and careful scheduling help optimize limited specialized resources.',
            'consequence_a': 'Chaos ensues with uncoordinated work',
            'consequence_b': 'Work progresses efficiently with optimal resource use',
            'consequence_c': 'Not a realistic solution',
            'consequence_d': 'Important restoration work remains incomplete'
        },
        {
            'scenario_title': 'Stakeholder Management',
            'scenario': 'Royal family members have conflicting views on restoration priorities.',
            'text': 'How do you handle stakeholder conflicts?',
            'option_a': 'Follow only the king\'s orders',
            'option_b': 'Document all viewpoints and facilitate consensus through structured discussions',
            'option_c': 'Ignore the conflicts and proceed with your own plan',
            'option_d': 'Postpone the project until everyone agrees',
            'correct_option': 'B',
            'explanation': 'Stakeholder conflicts require documentation and facilitated discussion to reach consensus.',
            'consequence_a': 'Creates resentment and resistance from other stakeholders',
            'consequence_b': 'Achieves buy-in and support from all stakeholders',
            'consequence_c': 'Leads to project opposition and interference',
            'consequence_d': 'Project never progresses'
        }
    ]
    
    for q_data in questions:
        Question.objects.create(
            mission=castle_mission,
            **q_data
        )
create_castle_restoration_questions.short_description = "Create Castle Restoration Mission Questions"

def create_grand_tournament_questions(modeladmin, request, queryset):
    """Bulk create questions for Grand Tournament mission"""
    tournament_mission = Mission.objects.get(mission_type='GRAND_TOURNAMENT')
    
    questions = [
        {
            'scenario_title': 'Communication Plan',
            'scenario': 'Knights from multiple kingdoms are arriving for the tournament.',
            'text': 'How do you ensure effective communication?',
            'option_a': 'Create a comprehensive communication plan with multiple channels',
            'option_b': 'Let each kingdom handle their own communications',
            'option_c': 'Use only written announcements',
            'option_d': 'Communicate only with kingdom leaders',
            'correct_option': 'A',
            'explanation': 'A comprehensive communication plan ensures all stakeholders receive necessary information through appropriate channels.',
            'consequence_a': 'Tournament runs smoothly with well-informed participants',
            'consequence_b': 'Confusion and misunderstandings arise',
            'consequence_c': 'Many participants miss important updates',
            'consequence_d': 'Information fails to reach key participants'
        },
        {
            'scenario_title': 'Leadership Challenge',
            'scenario': 'Tournament staff includes people from different cultures and backgrounds.',
            'text': 'What leadership approach should you adopt?',
            'option_a': 'Use a single leadership style for everyone',
            'option_b': 'Adapt leadership style based on team needs and cultural contexts',
            'option_c': 'Delegate all leadership to local team leaders',
            'option_d': 'Minimize interaction with the team',
            'correct_option': 'B',
            'explanation': 'Effective leadership requires adapting to different cultural contexts and team needs.',
            'consequence_a': 'Some team members feel misunderstood and demotivated',
            'consequence_b': 'Team performs effectively with high morale',
            'consequence_c': 'Lack of coordination between teams',
            'consequence_d': 'Team lacks direction and motivation'
        },
        {
            'scenario_title': 'Stakeholder Management',
            'scenario': 'Different kingdoms have varying expectations for the tournament.',
            'text': 'How do you manage these expectations?',
            'option_a': 'Focus only on the host kingdom\'s expectations',
            'option_b': 'Document and analyze all stakeholder requirements',
            'option_c': 'Tell stakeholders to lower their expectations',
            'option_d': 'Promise to meet all expectations',
            'correct_option': 'B',
            'explanation': 'Successful stakeholder management requires understanding and balancing different expectations.',
            'consequence_a': 'Other kingdoms feel ignored and withdraw',
            'consequence_b': 'Tournament satisfies key stakeholder needs',
            'consequence_c': 'Damages relationships with participating kingdoms',
            'consequence_d': 'Sets unrealistic expectations leading to disappointment'
        },
        {
            'scenario_title': 'Risk Response',
            'scenario': 'Weather forecast predicts storms during the tournament.',
            'text': 'What risk response strategy is most appropriate?',
            'option_a': 'Cancel the tournament',
            'option_b': 'Develop contingency plans for indoor and outdoor events',
            'option_c': 'Ignore the forecast',
            'option_d': 'Schedule all events for early morning',
            'correct_option': 'B',
            'explanation': 'Contingency planning allows for flexible response to weather risks while maintaining event objectives.',
            'consequence_a': 'Wastes preparation effort and disappoints participants',
            'consequence_b': 'Tournament succeeds regardless of weather',
            'consequence_c': 'Events are disrupted by weather',
            'consequence_d': 'Creates scheduling conflicts and logistical problems'
        },
        {
            'scenario_title': 'Conflict Resolution',
            'scenario': 'Two kingdoms dispute tournament rules interpretation.',
            'text': 'How do you resolve this conflict?',
            'option_a': 'Side with the host kingdom',
            'option_b': 'Facilitate a discussion and document agreed interpretations',
            'option_c': 'Ignore the dispute',
            'option_d': 'Create new rules on the spot',
            'correct_option': 'B',
            'explanation': 'Transparent conflict resolution and documentation help prevent future disputes.',
            'consequence_a': 'Creates resentment and potential withdrawal',
            'consequence_b': 'Establishes clear understanding and fairness',
            'consequence_c': 'Dispute escalates during tournament',
            'consequence_d': 'Causes confusion and more conflicts'
        }
    ]
    
    for q_data in questions:
        Question.objects.create(
            mission=tournament_mission,
            **q_data
        )
create_grand_tournament_questions.short_description = "Create Grand Tournament Mission Questions"