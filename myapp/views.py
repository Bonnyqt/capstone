import json
from datetime import date
import logging
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.models import User as DjangoUser
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib import messages
from django.views import View
from .models import CanvasStateDefend, Feedback, StudentAnalysis
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from .tokens import account_activation_token
from django.contrib.sites.shortcuts import get_current_site
from django.utils.html import strip_tags
from django.contrib.sites.models import Site
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings
from django.utils import timezone
from .models import ActivityLog
from pytz import timezone as pytz_timezone  
from django.views.decorators.csrf import csrf_exempt
from .models import UserProfile
from .forms import UserProfileForm
from django.http import HttpResponseNotFound
from django.contrib.auth.models import User
from django.db.models.functions import TruncMonth
from django.db.models import Count
from .models import EmailLog
from .models import BlogPost
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import EmailLog
from collections import Counter
import random
import string
from django.db.models import Q
from .models import CanvasState
from django.views.decorators.http import require_POST
from .models import Score 
from django.utils.timezone import now
from django.db import models
from .models import UserSession
import openai
from .models import Analysis
import hashlib
from django.db.models.functions import TruncMonth
from .models import Course
import pandas as pd
from django.http import HttpResponse
from dotenv import load_dotenv
import os

# Load the .env file
load_dotenv()

# Access the OpenAI API key
openai.api_key = os.getenv('OPENAI_API_KEY')



def generate_analysis(data, chart_type):
    """
    Generate an analysis based on the provided data and chart type.
    - `data`: Data to be analyzed.
    - `chart_type`: The type of chart (e.g., 'pie_chart', 'bar_chart', 'area_chart', 'split_graph').
    """
    if not data:
        return "No data provided for analysis."
    
    prompt = ""

    if chart_type == 'pie_chart':
        prompt = f"Based on the following data for the pie chart, provide a detailed analysis:\n{data}\nAnalysis:"
    elif chart_type == 'bar_chart':
        prompt = f"Based on the following data for the bar chart, provide a detailed analysis:\n{data}\nAnalysis:"
    elif chart_type == 'area_chart':
        prompt = f"Based on the following data for the area chart, provide a detailed analysis:\n{data}\nAnalysis:"
    elif chart_type == 'split_graph':
        prompt = f"Based on the following data for the split pane graph, in 3-4 sentences provide a detailed analysis:\n{data}\nAnalysis:"
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # Use "gpt-4" if available
        messages=[{
            "role": "system", 
            "content": "You are a helpful assistant for generating descriptive analytics"
        }, {
            "role": "user", 
            "content": prompt
        }],
        max_tokens=500,
        temperature=0.7,
    )

    return response['choices'][0]['message']['content'].strip()



# Function to generate checksum for data
def generate_data_checksum(data):
    """Generate a checksum for the data to track changes"""
    data_str = json.dumps(data, sort_keys=True)
    return hashlib.md5(data_str.encode('utf-8')).hexdigest()




@csrf_exempt
def submit_score(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        canvas_state_id = data.get('canvas_state_id')
        user_wires = json.loads(data.get('user_wires', '[]'))
        canvas_explanation = data.get('canvas_explanation', '')

        try:
            canvas_state = CanvasState.objects.get(id=canvas_state_id)
            correct_wires = canvas_state.wires

            normalized_correct_wires = {tuple(sorted([wire['start'], wire['end']])) for wire in correct_wires}
            normalized_user_wires = {tuple(sorted([wire['start'], wire['end']])) for wire in user_wires}

            correct_submissions = normalized_correct_wires & normalized_user_wires
            incorrect_submissions = normalized_user_wires - normalized_correct_wires

            # Calculate the score based on correct submissions
            total_score = len(correct_submissions) * 10

            # Calculate the total possible correct answers and total possible score
            total_possible_correct_answers = len(normalized_correct_wires)
            total_possible_score = total_possible_correct_answers * 10

            # Save the score and additional details
            Score.objects.create(
                user=request.user,
                score=total_score,
                category=canvas_state.category,
                correct_submissions=len(correct_submissions),
                incorrect_submissions=len(incorrect_submissions),
                canvas_state_title=canvas_state.title,
                finished=True,
                canvas_explanation=canvas_explanation,
                total_possible_score=total_possible_score,
                total_possible_correct_answers=total_possible_correct_answers,
            )

            return JsonResponse({
                'success': True,
                'score': total_score,
                'correct_wires': ['-'.join(wire) for wire in correct_submissions],
                'incorrect_wires': ['-'.join(wire) for wire in incorrect_submissions],
                'total_possible_score': total_possible_score,
                'total_possible_correct_answers': total_possible_correct_answers,
            })

        except CanvasState.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'CanvasState not found.'})

    return JsonResponse({'success': False, 'message': 'Invalid request method.'})




import datetime


def generate_network(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        title = data.get('title')
        prompt = data.get('prompt')
        category = data.get('category')
        difficulty = data.get('difficulty')
        canvas_time = data.get('canvas_time')
        canvas_sections = data.get('canvas_section')
        canvas_scenario = data.get('canvas_scenario', '').strip()
        canvas_deadline = data.get('canvas_deadline')  # Get the deadline from the frontend
        canvas_sections_str = ','.join(canvas_sections)

        try:
            # Parse deadline into a datetime object if provided
            due_date = None
            if canvas_deadline:
                due_date = datetime.datetime.fromisoformat(canvas_deadline)

            # Generate scenario if canvasScenario is empty
            if not canvas_scenario:
                scenario_prompt = (
                    f"Generate a realistic and detailed scenario for a network titled '{title}' in 3-4 sentences, and ender 'Create an attacking and defending network simulation using the tools provided.'"
      
                )
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are an assistant that writes realistic cybersecurity scenarios."},
                        {"role": "user", "content": scenario_prompt}
                    ],
                    max_tokens=200
                )
                canvas_scenario = response['choices'][0]['message']['content'].strip()

            # Call OpenAI API to generate the network
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that generates network nodes and wires. Each node should have an id, iconClass(fas fa), title(name of the node), ipAddress(IP: ), tooltip(the flow of the network), vulnerability (Vuln: High, Medium, Low), and position (random position: left, top). Each wire connects two nodes using start and end (like id: node-0) and has coordinates (startX, startY, endX, endY). Only return the JSON object with 'nodes' and 'wires'."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000
            )

            # Get the JSON response from OpenAI
            ai_generated_json = json.loads(response['choices'][0]['message']['content'].strip())

            # Extract nodes and wires
            nodes = ai_generated_json.get('nodes', [])
            wires = ai_generated_json.get('wires', [])

            # Adjust positions for nodes
            node_positions = calculate_positions(len(nodes))
            for idx, node in enumerate(nodes):
                position = node_positions[idx]
                node['left'] = f"{position['left']}px"
                node['top'] = f"{position['top']}px"

            # Adjust wire connections to match node positions
            for wire in wires:
                start_node = next((node for node in nodes if node['id'] == wire['start']), None)
                end_node = next((node for node in nodes if node['id'] == wire['end']), None)

                if start_node and end_node:
                    wire['startX'] = int(start_node['left'].replace('px', '')) + 25  # Adjust for node center
                    wire['startY'] = int(start_node['top'].replace('px', '')) + 25  # Adjust for node center
                    wire['endX'] = int(end_node['left'].replace('px', '')) + 25
                    wire['endY'] = int(end_node['top'].replace('px', '')) + 25

            # Store in the database
            canvas_state = CanvasState.objects.create(
                user=request.user,
                title=title,
                category=category,
                difficulty=difficulty,
                canvas_section=canvas_sections_str,
                canvas_time=canvas_time,
                canvas_scenario=canvas_scenario,
                due_date=due_date,  # Save the deadline
                nodes=nodes,
                wires=wires
            )

            return JsonResponse({'success': True})

        except Exception as e:
            print(f"Error: {e}")
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request method'})

def generate_network_defend(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        title = data.get('title')
        prompt = data.get('prompt')
        category = data.get('category')
        difficulty = data.get('difficulty')
        canvas_time = data.get('canvas_time')
        canvas_sections = data.get('canvas_section')
        canvas_sections_str = ','.join(canvas_sections)
        try:
            # Call OpenAI API to generate the network
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that generates network nodes and wires. Each node should have an id, iconClass(fas fa), title(name of the node), ipAddress(IP: ), tooltip(the flow of the network), vulnerability (Vuln: High, Medium, Low), and position (random position: left, top). Each wire connects two nodes using start and end (like id: node-0) and has coordinates (startX, startY, endX, endY). Only return the JSON object with 'nodes' and 'wires'."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000
            )

            # Get the JSON response from OpenAI
            ai_generated_json = json.loads(response['choices'][0]['message']['content'].strip())

            # Extract nodes and wires
            nodes = ai_generated_json.get('nodes', [])
            wires = ai_generated_json.get('wires', [])

            # Adjust positions for nodes
            node_positions = calculate_positions(len(nodes))
            for idx, node in enumerate(nodes):
                position = node_positions[idx]
                node['left'] = f"{position['left']}px"
                node['top'] = f"{position['top']}px"

            # Adjust wire connections to match node positions
            for wire in wires:
                start_node = next((node for node in nodes if node['id'] == wire['start']), None)
                end_node = next((node for node in nodes if node['id'] == wire['end']), None)

                if start_node and end_node:
                    wire['startX'] = int(start_node['left'].replace('px', '')) + 25  # Adjust for node center
                    wire['startY'] = int(start_node['top'].replace('px', '')) + 25  # Adjust for node center
                    wire['endX'] = int(end_node['left'].replace('px', '')) + 25
                    wire['endY'] = int(end_node['top'].replace('px', '')) + 25

            # Store in the database
            canvas_state = CanvasStateDefend.objects.create(
                user=request.user,
                title=title,
                category = category,
                difficulty = difficulty,
                canvas_section = canvas_sections_str,
                canvas_time = canvas_time,
                nodes=nodes,
                wires=wires
            )
            return JsonResponse({'success': True})

        except Exception as e:
            print(f"Error: {e}")
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request method'})


def calculate_positions(node_count):
    """
    Calculate positions for nodes in a grid or circular pattern.
    """
    positions = []
    grid_size = int(node_count ** 0.5) + 1  # Grid size for arranging nodes
    spacing = 150  # Space between nodes

    for idx in range(node_count):
        row = idx // grid_size
        col = idx % grid_size
        positions.append({
            'left': col * spacing + 50,  # Offset to prevent nodes from starting at the edge
            'top': row * spacing + 50
        })

    return positions



@login_required
def admin_dashboard(request):
    if not request.user.is_superuser:
        return redirect('index')
    users = User.objects.filter(is_superuser=False)
    student_count = User.objects.filter(is_superuser=False).exclude(email__endswith='.it@tip.edu.ph').filter(email__endswith='@tip.edu.ph').count()
    student_status = User.objects.filter(userprofile__is_online=True, is_superuser=False).exclude(email__endswith='.it@tip.edu.ph').filter(email__endswith='@tip.edu.ph').count()
    professor_count = User.objects.filter(is_superuser=False, email__endswith='.it@tip.edu.ph').count()
    category_submission_counts = Score.objects.values('category') \
        .annotate(submission_count=Count('category')) \
        .order_by('category')
    challenges = CanvasState.objects.all()
    count_challenges = challenges.count()
    challengesdefend = CanvasStateDefend.objects.all()
    count_challengesdefend = challengesdefend.count()
    total_count = count_challenges + count_challengesdefend
    categories = [entry['category'] for entry in category_submission_counts]
    submission_counts = [entry['submission_count'] for entry in category_submission_counts]
    user_scores = Score.objects.values('user') \
        .annotate(total_score=Sum('score')) \
        .order_by('-total_score')
    users_names = [User.objects.get(id=entry['user']).username for entry in user_scores]
    total_scores = [entry['total_score'] for entry in user_scores]
    is_superuser = [user.is_superuser for user in users]
    data_for_analysis_pie = {
        "Submission Counts by Category": dict(zip(categories, submission_counts)),
    }
    data_for_analysis_bar = {
        "Users and Total Scores": dict(zip(users_names, total_scores)),
    }
    
    registrations_data = User.objects.annotate(
    registration_month=TruncMonth('date_joined')
    ).values('registration_month').annotate(
    student_count=Count('id', filter=Q(email__endswith='@tip.edu.ph') & ~Q(email__endswith='.it@tip.edu.ph')),
    professor_count=Count('id', filter=Q(email__endswith='.it@tip.edu.ph'))
    ).order_by('registration_month')
    registration_dates = [entry['registration_month'].strftime('%Y-%m-%d') if entry['registration_month'] else None for entry in registrations_data]
    student_registrations = [entry['student_count'] for entry in registrations_data]
    professor_registrations = [entry['professor_count'] for entry in registrations_data]
    area_chart_data = {
        "registration_dates": registration_dates,
        "student_registrations": student_registrations,
        "professor_registrations": professor_registrations,
    }
    split_pane_data = (
            Score.objects
            .values('category')
            .annotate(
                total_correct=Sum('correct_submissions'),
                total_incorrect=Sum('incorrect_submissions')
            )
        )
    split_graph_data = {
    entry['category']: {
        "total_correct": entry['total_correct'] or 0,  # Handle None values
        "total_incorrect": entry['total_incorrect'] or 0,  # Handle None values
    }
    for entry in split_pane_data
}
    area_analysis = generate_area_analysis(area_chart_data)
    data_for_analysis_area = {
        "Registrations Over Time": area_chart_data,
    }
    current_checksum = generate_data_checksum({
        "Pie Chart Data": data_for_analysis_pie,
        "Bar Chart Data": data_for_analysis_bar,
        "Area Chart Data": data_for_analysis_area,
        "Split Pane Data": split_graph_data,  # Include the new split graph data
    })
    latest_analysis = Analysis.objects.order_by('-created_at').first()
    if latest_analysis and latest_analysis.data_checksum == current_checksum:
        pie_analysis = latest_analysis.pie_graph
        bar_analysis = latest_analysis.bar_graph
        area_analysis = latest_analysis.areachart_graph if latest_analysis.areachart_graph else "Not Generated Yet"
        split_analysis = latest_analysis.split_graph or "Not Generated Yet"
    else:
        pie_analysis = generate_analysis(data_for_analysis_pie, 'pie_chart')
        bar_analysis = generate_analysis(data_for_analysis_bar, 'bar_chart')
        area_analysis = generate_analysis(data_for_analysis_area, 'area_chart')
        split_analysis = generate_analysis(split_graph_data, 'split_graph')

        Analysis.objects.create(
            pie_graph=pie_analysis,
            bar_graph=bar_analysis,
            areachart_graph=area_analysis,
            split_graph=split_analysis,
            data_checksum=current_checksum
        )
    textAnalytics = Analysis.objects.last()
    top_challenge = Score.objects.values('canvas_state_title') \
                                 .annotate(total_count=Count('canvas_state_title')) \
                                 .order_by('-total_count') \
                                 .first()
    top_category = Score.objects.values('category') \
                                .annotate(total_count=Count('category')) \
                                .order_by('-total_count') \
                                .first()
    return render(request, 'myapp/admin/admin_dashboard.html', {
        'users': users,
        'student_status': student_status,
        'student_count': student_count,
        'professor_count': professor_count,
        'categories': categories,
        'top_category': top_category,
        'submission_counts': submission_counts,
        'users_names': users_names,
        'total_count': total_count,
        'total_scores': total_scores,
        'is_superuser': is_superuser,
        'pie_analysis': pie_analysis,
        'bar_analysis': bar_analysis,
        'top_challenge': top_challenge,
        'area_analysis': area_analysis,
        'textAnalytics': textAnalytics,
        'analysis_created_at': textAnalytics.created_at if textAnalytics else None,   
    })

import openai
def student_analysis(logged_in_user):
    """
    Perform analysis for split pane graph and pie chart, and save the results in the database for the logged-in user.
    """
    try:
        # Ensure `logged_in_user` is a `User` instance
        if isinstance(logged_in_user, int):  # If user ID is provided
            logged_in_user = User.objects.get(pk=logged_in_user)

        # === Split Pane Graph Data ===
        split_pane_data = (
            Score.objects.filter(user=logged_in_user)  # Filter by the logged-in user
            .values('category')
            .annotate(
                total_correct=Sum('correct_submissions'),
                total_incorrect=Sum('incorrect_submissions')
            )
        )

        if not split_pane_data.exists():
            return "No submission data found to analyze."

        split_pane_data_str = "\n".join(
            f"Category: {entry['category']}, Correct: {entry['total_correct']}, Incorrect: {entry['total_incorrect']}"
            for entry in split_pane_data
        )

          # Replace with your OpenAI API key
        split_pane_prompt = (
            f"The following is data about user performance categorized by topic:\n"
            f"{split_pane_data_str}\n"
            "Generate a concise, insightful analysis highlighting the user's strengths, weaknesses, and areas for improvement."
        )

        split_pane_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert data analyst, in 3-4 sentences analysis."},
                {"role": "user", "content": split_pane_prompt},
            ],
            max_tokens=200,
        )
        split_graph_analysis = split_pane_response['choices'][0]['message']['content'].strip()

        # === Pie Chart Data ===
        category_counts = (
            Score.objects.filter(user=logged_in_user)
            .values('category')
            .annotate(count=Count('id'))  # Count the entries for each category
        )

        total_categories = len(category_counts)  # Total unique categories
        total_answers = sum(entry['count'] for entry in category_counts)  # Total submissions
        most_answered_category = max(category_counts, key=lambda x: x['count'], default=None)

        # Prepare data for OpenAI prompt
        pie_chart_data_str = (
            f"The user has answered {total_answers} questions across {total_categories} categories. "
            f"The most answered category is '{most_answered_category['category']}' with {most_answered_category['count']} answers."
            if most_answered_category
            else "The user has not answered enough questions to determine a most answered category."
        )

        # Use OpenAI to generate Pie Chart analysis
        pie_chart_prompt = (
            f"The following is data about a user's category-wise performance:\n"
            f"{pie_chart_data_str}\n"
            "Write an engaging and insightful analysis for a profile report."
        )

        pie_chart_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert data analyst, in 3-4 sentences analysis."},
                {"role": "user", "content": pie_chart_prompt},
            ],
            max_tokens=150,
        )
        pie_chart_analysis = pie_chart_response['choices'][0]['message']['content'].strip()

        # Generate a checksum for deduplication
        data_checksum = generate_data_checksum(split_pane_data_str + pie_chart_data_str)

        # Save analyses to the database for the logged-in user
        analysis, created = StudentAnalysis.objects.get_or_create(
            user=logged_in_user, data_checksum=data_checksum
        )
        analysis.split_graph = split_graph_analysis  # Store Split Pane Graph analysis
        analysis.pie_graph = pie_chart_analysis  # Store Pie Chart analysis
        analysis.save()

        return "Analysis for split pane graph and pie chart saved successfully."
    except User.DoesNotExist:
        return "Invalid user ID provided. User does not exist."
    except Exception as e:
        print(f"Error in student_analysis: {e}")
        return "An error occurred during analysis."







def export_data_to_excel(request):
    current_date = timezone.now().date()
    student_count = UserProfile.objects.filter(program='student').count() 
    professor_count = UserProfile.objects.filter(program='professor').count()  
    active_users = User.objects.filter(is_active=True).count()
    challenge_count = UserProfile.objects.filter(is_online=True).count()
    daily_category_submission = Score.objects.filter(created_at__date=current_date).values('category').annotate(submission_count=Count('id'))
    daily_score_submission = Score.objects.filter(created_at__date=current_date).values('score').annotate(submission_count=Count('id'))
    data = {
        'Student Count': [student_count],
        'Professor Count': [professor_count],
        'Active Users': [active_users],
        'Challenge Count': [challenge_count],
    }

    # Add daily category submissions data to the export (flattened for simplicity)
    for submission in daily_category_submission:
        category = submission['category']
        submission_count = submission['submission_count']
        data[f"Category Submission - {category}"] = [submission_count]

    # Add daily score submissions data to the export (flattened for simplicity)
    for submission in daily_score_submission:
        score = submission['score']
        submission_count = submission['submission_count']
        data[f"Score Submission - {score}"] = [submission_count]

    # Convert the data dictionary into a pandas DataFrame
    df = pd.DataFrame(data)

    # Create an HttpResponse object for Excel export
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=data_report.xlsx'

    # Write DataFrame to Excel file
    with pd.ExcelWriter(response, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Report Data')

    return response


def generate_area_analysis(data):
    """Generate detailed analysis for area chart data."""
    student_growth = f"Student registrations increased by {sum(data['student_registrations'])} over the time period."
    professor_growth = f"Professor registrations increased by {sum(data['professor_registrations'])} over the same period."
    
    return f"Area Chart Analysis:\n\nStudent Registration Trends: {student_growth}\nProfessor Registration Trends: {professor_growth}"
@login_required
def update_window_state(request):
    if request.method == 'POST':
        # Handle window state update when a window is opened or closed
        user_session, created = UserSession.objects.get_or_create(user=request.user)
        window_open = request.POST.get('window_open') == 'true'
        user_session.window_open = window_open
        user_session.save()
        return JsonResponse({'status': 'success'})

    elif request.method == 'GET':
        # Handle window state check when the page loads
        user_session, created = UserSession.objects.get_or_create(user=request.user)
        return JsonResponse({'window_open': user_session.window_open})

    return JsonResponse({'status': 'failed'}, status=400)

@csrf_exempt  
def save_score(request):
    if request.method == 'POST':
        try:
            # Parse the incoming JSON data
            data = json.loads(request.body)
            score = data.get('score', 0)
            finished = data.get('finished', False)  # Get the 'finished' status from the request
            category = data.get('category', '')  # Get the category from the request
            correct_submissions = data.get('correct_submissions', 0)  # Get correct submissions count
            incorrect_submissions = data.get('incorrect_submissions', 0)  # Get incorrect submissions count
            canvas_state_title = data.get('canvas_state_title', '')  # Get the canvas state title from the request

            # Check if user is authenticated
            if not request.user.is_authenticated:
                return JsonResponse({'status': 'failed', 'message': 'User not authenticated'}, status=401)
            
            # Save the score to the database with user, date_submitted, finished status, category, and submission counts
            user_score = Score.objects.create(
                user=request.user,  # Associate the score with the logged-in user
                score=score,
                date_submitted=now().date(),  # Use current date as submission date
                finished=finished,  # Save the finished status
                category=category,  # Save the category
                correct_submissions=correct_submissions,  # Save the correct submissions count
                incorrect_submissions=incorrect_submissions,  # Save the incorrect submissions count
                canvas_state_title=canvas_state_title  # Save the canvas state title
            )
            
            return JsonResponse({
                'status': 'success',
                'score': user_score.score,
                'finished': user_score.finished,
                'category': user_score.category,
                'user': request.user.username,
                'correct_submissions': user_score.correct_submissions,
                'incorrect_submissions': user_score.incorrect_submissions
            })
        except Exception as e:
            return JsonResponse({'status': 'failed', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'failed', 'message': 'Invalid request method'}, status=400)



def remove_news(request, canvas_id):
    # Get the CanvasState object or return 404 if not found
    canvas_state = get_object_or_404(BlogPost, id=canvas_id)
    
    # Delete the canvas state
    canvas_state.delete()

    # Redirect to a page (e.g., a list of challenges or a success message)
    return redirect('news') 


def remove_challenge(request, canvas_id):
    # Get the CanvasState object or return 404 if not found
    canvas_state = get_object_or_404(CanvasState, id=canvas_id)
    
    # Delete the canvas state
    canvas_state.delete()

    # Redirect to a page (e.g., a list of challenges or a success message)
    return redirect('professor_view_challenges') 
def remove_challenge_defend(request, canvas_id):
    # Get the CanvasState object or return 404 if not found
    canvas_state = get_object_or_404(CanvasStateDefend, id=canvas_id)
    
    # Delete the canvas state
    canvas_state.delete()

    # Redirect to a page (e.g., a list of challenges or a success message)
    return redirect('professor_view_challenges')
from .models import CanvasState, Score, CanvasInteraction
from django.shortcuts import get_object_or_404, redirect, render
from .models import CanvasState, Score, CanvasInteraction

from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from myapp.models import CanvasState, Score, CanvasInteraction

def display_canvas(request, canvas_id):
    if not request.user.is_authenticated:
        return redirect('index')  # Redirect to the index page if not authenticated

    # Get the canvas state from the database, return 404 if not found
    canvas_state = get_object_or_404(CanvasState, id=canvas_id)

    # Check if the challenge is overdue based on the due date
    current_time = timezone.now()
    if canvas_state.due_date and canvas_state.due_date < current_time:
        return redirect('simulate')  # Redirect if the challenge is overdue

    # Check if the user has already finished this challenge
    user_score = Score.objects.filter(user=request.user, canvas_state_title=canvas_state.title).first()
    if user_score and user_score.finished:
        return redirect('simulate')  # Redirect to simulate page if the challenge is finished

    # Track canvas interaction - increment access count and handle locking
    canvas_interaction, created = CanvasInteraction.objects.get_or_create(
        user=request.user, canvas_state=canvas_state
    )

    if created:  # If the interaction is newly created, initialize the access_count to 1
        canvas_interaction.access_count = 1
        canvas_interaction.save()
    else:  # If the interaction already exists, increment the access count
        canvas_interaction.access_count += 1
        canvas_interaction.save()

        # Lock the canvas if access count exceeds 3
        if canvas_interaction.access_count >= 1000:
            # Lock the canvas state
            canvas_interaction.locked = True
            canvas_interaction.save()

            # Optionally, log or send feedback for the user if desired
            print(f"Canvas {canvas_state.title} has been locked after {canvas_interaction.access_count} accesses.")

    # Redirect to simulate if the canvas is locked
    if canvas_interaction.locked:
        return redirect('simulate')

    # Prepare the canvas state data, including the canvas time
    canvas_state_data = {
        'category': canvas_state.category,
        'title': canvas_state.title,
        'nodes': canvas_state.nodes,  # Directly use the Python list from JSONField
        'wires': canvas_state.wires,  # Directly use the Python list from JSONField
        'canvas_time': canvas_state.canvas_time,
        'canvas_id': canvas_id,
        'canvas_scenario': canvas_state.canvas_scenario,
    }

    # Render the template with the canvas state data
    return render(request, 'myapp/display_canvas.html', {'canvas_state': canvas_state_data})






def display_canvas_defend(request, canvas_id):
    if not request.user.is_authenticated:
        return redirect('index')  # Redirect to the index page if not authenticated

    # Get the canvas state from the database, return 404 if not found
    canvas_state_defend = get_object_or_404(CanvasStateDefend, id=canvas_id)

    # Check if the user has already finished this challenge
    user_score = Score.objects.filter(user=request.user, canvas_state_title=canvas_state_defend.title).first()
    if user_score and user_score.finished:
        return redirect('simulate')  # Redirect to simulate page if the challenge is finished

    # Track canvas interaction - increment access count and handle locking
    canvas_interaction, created = CanvasInteraction.objects.get_or_create(
        user=request.user, canvas_state_defend=canvas_state_defend  # Use canvas_state_defend instead of canvas_state
    )

    if created:  # If the interaction is newly created, initialize the access_count to 1
        canvas_interaction.access_count = 1
        canvas_interaction.save()
    else:  # If the interaction already exists, increment the access count
        canvas_interaction.access_count += 1
        canvas_interaction.save()

        # Lock the canvas if access count exceeds 3
        if canvas_interaction.access_count >= 3:
            # Lock the canvas interaction
            canvas_interaction.locked = True
            canvas_interaction.save()

            # Optionally, lock the canvas state as well
            canvas_state_defend.locked = True
            canvas_state_defend.save()

            # Optionally, log or send feedback for the user if desired
            print(f"Canvas {canvas_state_defend.title} has been locked after {canvas_interaction.access_count} accesses.")
    if canvas_interaction.locked:
        return redirect('simulate_defend')
    # Prepare the canvas state data, including the canvas time
    canvas_state_data = {
        'category': canvas_state_defend.category,
        'title': canvas_state_defend.title,
        'nodes': canvas_state_defend.nodes,  # Directly use the Python list from JSONField
        'wires': canvas_state_defend.wires,  # Directly use the Python list from JSONField
        'canvas_time': canvas_state_defend.canvas_time  # Include the canvas time from the database
    }

    # Render the template with the canvas state data
    return render(request, 'myapp/display_canvas_defend.html', {'canvas_state': canvas_state_data})


@csrf_exempt
def save_canvas_state(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        
        # Retrieve data from the request
        title = data.get('title')
        category = data.get('category')
        difficulty = data.get('difficulty')
        canvas_time = data.get('canvas_time')
        canvas_sections = data.get('canvas_section')
        nodes = data.get('nodes')
        wires = data.get('wires')
        due_date = data.get('due_date')
        canvas_scenario = data.get('canvas_scenario', '').strip()

        # If canvas_scenario is empty, generate it using GPT-3.5
        if not canvas_scenario:
            try:
                openai.api_key = os.getenv('OPENAI_API_KEY')
                prompt = f"Generate a realistic and detailed scenario for a network titled '{title}' in 3-4 sentences, and ender 'Create an attacking and defending network simulation using the tools provided.'"
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "system", "content": "You are an assistant that writes realistic cybersecurity scenarios."},
                              {"role": "user", "content": prompt}],
                    max_tokens=200
                )
                canvas_scenario = response['choices'][0]['message']['content'].strip()
            except Exception as e:
                return JsonResponse({'status': 'error', 'message': f'Error generating scenario: {str(e)}'})

        # Save sections as a string
        canvas_sections_str = ','.join(canvas_sections)

        # Save canvas state to the database
        try:
            canvas_state = CanvasState.objects.create(
                user=request.user,
                title=title,
                category=category,
                difficulty=difficulty,
                canvas_time=canvas_time,
                canvas_section=canvas_sections_str,
                nodes=nodes,
                wires=wires,
                due_date=due_date,
                canvas_scenario=canvas_scenario
            )
            return JsonResponse({'status': 'success', 'message': 'Canvas state saved successfully!'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': f'Error saving canvas state: {str(e)}'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})



def user_list(request):
    query = request.GET.get('q')
    if query:
        users = User.objects.filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query
        ))
    else:
        users = User.objects.all()

    context = {
        'users': users,
    }
    return render(request, 'myapp/other_profiles.html', context)


@csrf_exempt
def save_canvas_state_defend(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        title = data.get('title')
        category = data.get('category')
        difficulty = data.get('difficulty')
        canvas_time = data.get('canvas_time')
        canvas_sections = data.get('canvas_section')  # List of selected sections
        nodes = data.get('nodes')
        wires = data.get('wires')

        # Convert list of sections to comma-separated string
        canvas_sections_str = ','.join(canvas_sections)

        # Save the canvas state
        canvas_state = CanvasStateDefend.objects.create(
            user=request.user,
            title=title,
            category=category,
            difficulty=difficulty,
            canvas_time=canvas_time,
            canvas_section=canvas_sections_str,  # Store sections
            nodes=nodes,
            wires=wires
        )

        return JsonResponse({'status': 'success', 'message': 'Canvas state saved successfully!'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})



def reset_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            # Generate a temporary password
            temp_password = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
            # Send the temporary password to the user's email
            send_mail(
                'Password Reset',
                f'Your temporary password is: {temp_password}',
                'cyberclash.capstone@gmail.com',  # Replace with your email
                [email],
                fail_silently=False,
            )
            # Update the user's password in the database
            user.set_password(temp_password)
            user.save()
            return redirect('login')
        except User.DoesNotExist:
            return render(request, 'myapp/login.html', {'alert': 'Email not registered! Please register first'})
    return render(request, 'myapp/password_reset.html')

def add_news(request):
    if not request.user.is_superuser:
        return redirect('index') 
    if request.method == 'POST':
        title = request.POST.get('title')
        author = request.POST.get('author')
        date_published = request.POST.get('date_published')
        content = request.POST.get('content')
        image = request.FILES.get('image')
        url = request.POST.get('url')

        # Check if all required fields are provided
        if title and author and date_published and content and image:
            # Create and save the new blog post
            try:
                BlogPost.objects.create(
                    title=title,
                    author=author,
                    date_published=date_published,
                    content=content,
                    image=image,
                    url=url
                )
                messages.success(request, 'News added successfully.')
                return redirect('news')  # Redirect to news list
            except Exception as e:
                messages.error(request, f'Error adding news: {str(e)}')
        else:
            messages.error(request, 'Please fill out all fields.')

    return render(request, 'myapp/admin/news.html')

def news(request):
    if not request.user.is_superuser:
        return redirect('index') 
    feedbacks = Feedback.objects.all()  # Fetch all feedback
    feedback_count = feedbacks.count() 
    challenges = BlogPost.objects.all()
    canvas_states = BlogPost.objects.all()
    context = {
        'feedback_count':feedback_count,
        'feedbacks': feedbacks,
        'challenges': challenges,
        'canvas_states': canvas_states,
    }
    return render(request, 'myapp/admin/admin_news.html', context)


def user_search(request):
    if not request.user.is_superuser:
        return redirect('index') 
    query = request.GET.get('q', '')
    if query:
        users = User.objects.filter(
            first_name__icontains=query
        ) | User.objects.filter(
            email__icontains=query
        ) 
    else:
        users = User.objects.all()

    return render(request, 'myapp/admin/user_accounts.html', {'users': users})

def get_registration_data(request):
    if not request.user.is_superuser:
        return redirect('index') 
    # Query the database for registrations grouped by month
    registration_data = (
        User.objects
        .filter(is_superuser=False) 
        .annotate(month=TruncMonth('date_joined'))
        .values('month')
        .annotate(total=Count('id'))
        .order_by('month')
    )
    
    # Prepare the data for the chart
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    registration_counts = [0] * 12  # Initialize list with 12 zeroes for each month

    for data in registration_data:
        month_number = data['month'].month  # Get the month number (1-12)
        registration_counts[month_number - 1] = data['total']  # Subtract 1 because list is 0-indexed
    
    return JsonResponse({
        'labels': months,
        'data': registration_counts,
    })




from django.db.models import Sum, F
from .models import EmailLog, BlogPost, Score, User

def index(request):
    if request.user.is_authenticated:
        user = request.user
        # Filter emails for the logged-in user
        email_logs = EmailLog.objects.filter(recipients__icontains=user.email).order_by('-sent_at')
        # Count the number of new emails for the logged-in user
        email_count = EmailLog.objects.filter(recipients__icontains=user.email, is_new=True).count()

        # Calculate the total score for the logged-in user
        total_score = Score.objects.filter(user=user).aggregate(total=Sum('score'))['total'] or 0

        # Get all users and their scores, excluding users with the specific email domain
        user_scores = list(
            Score.objects.values('user')
            .annotate(total_score=Sum('score'))
            .order_by('-total_score')
            .exclude(user__email__endswith='.it@tip.edu.ph')  # Exclude users with this email domain
        )

        # Calculate the rank of the logged-in user
        rank = next((index + 1 for index, user_score in enumerate(user_scores) if user_score['user'] == user.id), 0)

        # Calculate the performance percentage
        total_correct = Score.objects.filter(user=user).aggregate(total_correct=Sum('correct_submissions'))['total_correct'] or 0
        total_submissions = Score.objects.filter(user=user).aggregate(total_submissions=Sum('correct_submissions') + Sum('incorrect_submissions'))['total_submissions'] or 1  # Avoid division by zero
    user_role = "Guest"  # Default role for unauthenticated users


    if request.user.is_authenticated:
        user_first_name = request.user.first_name
        if request.user.is_superuser:
            user_role = "Admin"
        elif request.user.email.endswith('.it@tip.edu.ph'):
            user_role = "Professor"
        else:
            user_role = "Student"
        performance_percentage = (total_correct / total_submissions) * 100 if total_submissions > 0 else 0
    else:
        # If the user is not logged in, show no emails and set score to 0
        email_logs = []
        email_count = 0
        total_score = 0
        rank = 0
        performance_percentage = 0

    blogposts = BlogPost.objects.all()  # Fetch all blog posts

    # Combine context dictionaries
    context = {
        'email_count': email_count,
        'user_role':user_role,
        'email_logs': email_logs,
        'blogposts': blogposts,  # Include blogposts in the context
        'total_score': total_score,  # Pass total score to the template
        'rank': rank,  # Pass rank to the template
        'performance_percentage': performance_percentage,  # Pass performance percentage to the template
    }

    return render(request, 'myapp/index.html', context)


    

def about(request):
    if request.user.is_authenticated:
        user = request.user
        # Filter emails for the logged-in user
        email_logs = EmailLog.objects.filter(recipients__icontains=user.email).order_by('-sent_at')
        
        # Count the number of new emails for the logged-in user
        email_count = EmailLog.objects.filter(recipients__icontains=user.email, is_new=True).count()
    else:
        # If the user is not logged in, show no emails
        email_logs = []
        email_count = 0
    user_role = "Guest"  # Default role for unauthenticated users


    if request.user.is_authenticated:
        user_first_name = request.user.first_name
        if request.user.is_superuser:
            user_role = "Admin"
        elif request.user.email.endswith('.it@tip.edu.ph'):
            user_role = "Professor"
        else:
            user_role = "Student"
    context = {
        'user_role':user_role,
        'email_count': email_count,
        'email_logs': email_logs,
 
    }
    return render(request, 'myapp/about.html', context)


def generate_encouraging_text(title):
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": f"Generate a clever and encouraging one-liner related to cybersecurity titled '{title}'."}
    ]
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # Or use the latest available model
        messages=messages,
        max_tokens=50,
        temperature=0.7
    )
    
    return response['choices'][0]['message']['content'].strip()

def simulate(request):
    if not request.user.is_authenticated:
        return redirect('index')  # Redirect to login or homepage if unauthenticated

    user = request.user

    # Fetch user's profile
    user_profile = UserProfile.objects.filter(user=user).first()

    # Check if profile setup is incomplete
    profile_incomplete = not (user_profile and user_profile.program and user_profile.section and user_profile.course_code)

    if profile_incomplete:
        return render(request, 'myapp/simulate.html', {
            'profile_incomplete': True,
            'email_count': 0,  # Or relevant default value
            'email_logs': [],  # Or relevant default value
        })

    # Filter emails for the logged-in user
    email_logs = EmailLog.objects.filter(recipients__icontains=user.email).order_by('-sent_at')

    # Count the number of new emails for the logged-in user
    email_count = EmailLog.objects.filter(recipients__icontains=user.email, is_new=True).count()

    # Fetch scores for the authenticated user
    user_scores = Score.objects.filter(user=user)

    # Check if the tutorial challenge is finished
    tutorial_title = "TUTORIAL"  # Replace with the exact fixed title of the tutorial challenge
    tutorial = CanvasState.objects.filter(title=tutorial_title).first()
    tutorial_finished = False
    if tutorial:
        tutorial_score = user_scores.filter(canvas_state_title=tutorial.title).first()
        tutorial_finished = tutorial_score.finished if tutorial_score else False

    # Filter canvas states to exclude the tutorial challenge
    canvas_states = CanvasState.objects.filter(
        Q(canvas_section__icontains="All") |
        Q(canvas_section__icontains=user_profile.section)
    ).exclude(title=tutorial_title)

    challenges = []

    current_time = timezone.now()  # Get the current time for overdue checking

    for canvas_state in canvas_states:
        score = user_scores.filter(canvas_state_title=canvas_state.title).first()
        finished = score.finished if score else False

        if canvas_state.created_at > user.last_login:
            if not canvas_state.title_definition:
                challenge_message = generate_encouraging_text(canvas_state.title)
                canvas_state.title_definition = challenge_message
                canvas_state.save()

        closed_by_user = score.finished if score else False

        # Check if the challenge is locked for the current user
        canvas_interaction = CanvasInteraction.objects.filter(user=user, canvas_state=canvas_state).first()
        is_locked = canvas_interaction.locked if canvas_interaction else False
        
        # Check if the challenge is overdue (only if due_date is not None)
        is_overdue = canvas_state.due_date and canvas_state.due_date < current_time

        challenges.append({
            'id': canvas_state.id,
            'title': canvas_state.title,
            'category': canvas_state.category,
            'difficulty': canvas_state.difficulty,
            'created_at': canvas_state.created_at,
            'due_date': canvas_state.due_date,
            'finished': finished,
            'title_definition': canvas_state.title_definition,
            'closed_by_user': closed_by_user,
            'locked': is_locked,  # Store the locked state for the challenge
            'is_overdue': is_overdue,  # Add the overdue state for each challenge
        })

    categories = set([challenge['category'] for challenge in challenges])
    user_role = "Guest"

    if request.user.is_authenticated:
        user_first_name = request.user.first_name
        if request.user.is_superuser:
            user_role = "Admin"
        elif request.user.email.endswith('.it@tip.edu.ph'):
            user_role = "Professor"
        else:
            user_role = "Student"

    context = {
        'challenges': challenges if tutorial_finished else [],  # Show challenges only if tutorial is finished
        'tutorial': tutorial if not tutorial_finished else None,  # Show tutorial if not finished
        'email_count': email_count,
        'email_logs': email_logs,
        'user_role': user_role,
        'categories': categories,
    }
    return render(request, 'myapp/simulate.html', context)




def mark_challenge_closed(request, canvas_id):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'User not authenticated'}, status=401)

    # Ensure we handle only POST requests
    if request.method == 'POST':
        user = request.user

        # Fetch or create the Score instance for the challenge
        canvas_state = CanvasState.objects.get(id=canvas_id)
        score, created = Score.objects.get_or_create(user=user, canvas_state_title=canvas_state.title)

        # Mark the challenge as closed by the user
        score.closed_by_user = True
        score.finished = True  # Mark it as finished, if necessary
        score.save()

        return JsonResponse({'status': 'success'})

    # Handle other request methods if needed
    return JsonResponse({'error': 'Invalid method'}, status=405)


def simulate_defend(request):
    if not request.user.is_authenticated:
        return redirect('index')  # Redirect to login or homepage if unauthenticated

    user = request.user

    # Fetch user's profile
    user_profile = UserProfile.objects.filter(user=user).first()

    # Check if profile setup is incomplete
    profile_incomplete = not (user_profile and user_profile.program and user_profile.section and user_profile.course_code)

    if profile_incomplete:
        return render(request, 'myapp/simulate.html', {
            'profile_incomplete': True,
            'email_count': 0,  # Or relevant default value
            'email_logs': [],  # Or relevant default value
        })

    # Filter emails for the logged-in user
    email_logs = EmailLog.objects.filter(recipients__icontains=user.email).order_by('-sent_at')

    # Count the number of new emails for the logged-in user
    email_count = EmailLog.objects.filter(recipients__icontains=user.email, is_new=True).count()

    # Fetch scores for the authenticated user
    user_scores = Score.objects.filter(user=user)

    # Check if the tutorial challenge is finished
    tutorial_title = "TUTORIAL"  # Replace with the exact fixed title of the tutorial challenge
    tutorial = CanvasStateDefend.objects.filter(title=tutorial_title).first()
    tutorial_finished = False
    if tutorial:
        tutorial_score = user_scores.filter(canvas_state_title=tutorial.title).first()
        tutorial_finished = tutorial_score.finished if tutorial_score else False

    # Filter canvas states to exclude the tutorial challenge
    canvas_states = CanvasStateDefend.objects.filter(
        Q(canvas_section__icontains="All") |
        Q(canvas_section__icontains=user_profile.section)
    ).exclude(title=tutorial_title)

    challenges = []

    for canvas_state in canvas_states:
        score = user_scores.filter(canvas_state_title=canvas_state.title).first()
        finished = score.finished if score else False

        if canvas_state.created_at > user.last_login:
            if not canvas_state.title_definition:
                challenge_message = generate_encouraging_text(canvas_state.title)
                canvas_state.title_definition = challenge_message
                canvas_state.save()

        closed_by_user = score.finished if score else False

        # Check if the challenge is locked for this user
        locked = CanvasInteraction.objects.filter(user=user, canvas_state_defend=canvas_state, locked=True).exists()

        challenges.append({
            'id': canvas_state.id,
            'title': canvas_state.title,
            'category': canvas_state.category,
            'difficulty': canvas_state.difficulty,
            'created_at': canvas_state.created_at,
            'finished': finished,
            'title_definition': canvas_state.title_definition,
            'closed_by_user': closed_by_user,
            'locked': locked,  # Add locked status to the challenge data
        })

    categories = set([challenge['category'] for challenge in challenges])
    user_role = "Guest"

    if request.user.is_authenticated:
        user_first_name = request.user.first_name
        if request.user.is_superuser:
            user_role = "Admin"
        elif request.user.email.endswith('.it@tip.edu.ph'):
            user_role = "Professor"
        else:
            user_role = "Student"

    context = {
        'challenges': challenges if tutorial_finished else [],  # Show challenges only if tutorial is finished
        'tutorial': tutorial if not tutorial_finished else None,  # Show tutorial if not finished
        'email_count': email_count,
        'email_logs': email_logs,
        'user_role': user_role,
        'categories': categories,
    }
    return render(request, 'myapp/simulate_defend.html', context)



@login_required
def leaderboards(request):
    if not request.user.is_authenticated:
        return redirect('index')  # Redirect if not authenticated

    user = request.user
    
    # Filter emails for the logged-in user
    email_logs = EmailLog.objects.filter(recipients__icontains=user.email).order_by('-sent_at')
    email_count = EmailLog.objects.filter(recipients__icontains=user.email, is_new=True).count() if user.is_authenticated else 0

    # Calculate total scores and order users by score in descending order, excluding superusers and emails ending with '.it@tip.edu.ph'
    user_scores = (
        Score.objects.values('user__id', 'user__first_name', 'user__email')
        .filter(~Q(user__email__endswith='.it@tip.edu.ph'))  # Exclude specific emails
        .filter(user__is_superuser=False)  # Exclude superusers
        .annotate(total_score=Sum('score'))  # Sum scores
        .order_by('-total_score')  # Sort by total scores
    )

    # Fetch profile images and other details for users
    user_profiles = UserProfile.objects.filter(user__id__in=[user['user__id'] for user in user_scores])
    profiles_dict = {profile.user.id: profile.profile_image.url for profile in user_profiles}

    # Include profile image URLs, rank, and top category in `user_scores`
    for idx, user_score in enumerate(user_scores, start=1):
        user_score['rank_no'] = idx  # Add rank number
        user_score['profile_image_url'] = profiles_dict.get(user_score['user__id'], '/media/profile_images/default_QBRSs97.jpg')  # Default image if not available
        user_score['username'] = user_score['user__email'].split('@')[0]  # Extract username before '@'

        # Assign ranks based on total score
        if user_score['total_score'] == 0:
            user_score['rank'] = "UNRANKED"
        elif 1 <= user_score['total_score'] <= 200:
            user_score['rank'] = "BEGINNER"
        elif 201 <= user_score['total_score'] <= 400:
            user_score['rank'] = "INTERMEDIATE"
        elif 401 <= user_score['total_score'] <= 600:
            user_score['rank'] = "ADVANCED"
        elif 601 <= user_score['total_score'] <= 800:
            user_score['rank'] = "EXPERT"
        elif 801 <= user_score['total_score'] <= 1000:
            user_score['rank'] = "PENETRATION TESTER"
        else:
            user_score['rank'] = "CERTIFIED ETHICAL HACKER"

        # Fetch and calculate the top category answered by the user
        user_canvas_states = Score.objects.filter(user_id=user_score['user__id']).values('category')
        if user_canvas_states.exists():
            category_counts = Counter(state['category'] for state in user_canvas_states)  # Count each category
            top_category = category_counts.most_common(1)  # Get the most common category
            user_score['top_category'] = top_category[0][0] if top_category else "N/A"
        else:
            user_score['top_category'] = "N/A"  # No categories answered

    # Fetch the top 3 users
    top_three = user_scores[:3]
    user_role = "Student"  # Default role

    if request.user.is_superuser:
        user_role = "Admin"
    elif request.user.email.endswith('.it@tip.edu.ph'):
        user_role = "Professor"
    context = {
        'top_three': top_three,
        'user_scores': user_scores,
        'email_count': email_count,
        'email_logs': email_logs,
        'user_role': user_role,
        'user':user
    }

    return render(request, 'myapp/leaderboards.html', context)


def contact(request):
    if request.user.is_authenticated:
        user = request.user
        # Filter emails for the logged-in user
        email_logs = EmailLog.objects.filter(recipients__icontains=user.email).order_by('-sent_at')
        
        # Count the number of new emails for the logged-in user
        email_count = EmailLog.objects.filter(recipients__icontains=user.email, is_new=True).count()
    else:
        # If the user is not logged in, show no emails
        email_logs = []
        email_count = 0

    user_role = "Guest"  # Default role for unauthenticated users


    if request.user.is_authenticated:
        user_first_name = request.user.first_name
        if request.user.is_superuser:
            user_role = "Admin"
        elif request.user.email.endswith('.it@tip.edu.ph'):
            user_role = "Professor"
        else:
            user_role = "Student"
    context = {
        'user_role':user_role,
        'email_count': email_count,
        'email_logs': email_logs,
    }
    return render(request, 'myapp/contact.html', context)

def loginPage(request):
    return render(request, 'myapp/login.html',)
def terms(request):
    return render(request, 'myapp/terms.html')

@login_required
def professor_add(request):
    # Check if the user is a superuser or if their email ends with '.it@tip.edu.ph'
    if not (request.user.is_superuser or request.user.email.endswith('.it@tip.edu.ph')):
        return redirect('index')  # Redirect to index if neither condition is met

    # Fetch all users or other logic here

    return render(request, 'myapp/professor/professor_add.html')
def professor_add_defense(request):
    if not (request.user.is_superuser or request.user.email.endswith('.it@tip.edu.ph')):
        return redirect('index')  # Redirect to index if neither condition is met
    return render(request, 'myapp/professor/professor_add_defense.html')

@login_required
def professor_announce(request):
    if not (request.user.is_superuser or request.user.email.endswith('.it@tip.edu.ph')):
        return redirect('index')  # Redirect to index if neither condition is met
    # Exclude superusers and users whose email ends with '.it@tip.edu.ph'
    users = User.objects.exclude(Q(is_superuser=True) | Q(email__endswith='.it@tip.edu.ph'))
    # Check if 'recipient' is passed in the query string
    recipient_email = request.GET.get('recipient')
    context = {
        'users': users,

        'selected_recipient': recipient_email,  # Pass the recipient email to the template
    }
    return render(request, 'myapp/professor/professor_announce.html', context)

@login_required
def professor_view_challenges(request):
    # Redirect if the user doesn't meet the required conditions
    if not (request.user.is_superuser or request.user.email.endswith('.it@tip.edu.ph')):
        return redirect('index')
    
    # Filter challenges based on the logged-in user
    challenges = CanvasState.objects.filter(user=request.user)
    canvas_states = CanvasStateDefend.objects.filter(user=request.user)  # Assuming similar structure

    context = {
        'challenges': challenges,
        'canvas_states': canvas_states,
    }
    return render(request, 'myapp/professor/professor_view_challenges.html', context)

    



import threading
from django.utils.timezone import now
from django.contrib.auth.models import User

def login(request):
    if request.method == 'POST':
        if 'login' in request.POST:
            # Handle login
            email = request.POST.get('email')
            password = request.POST.get('password')
            user = authenticate(request, username=email, password=password)
            if user is not None:
                auth_login(request, user)

                # Check if the user is a superuser (admin)
                if user.is_superuser:
                    return redirect('admin_dashboard')  # Redirect to admin dashboard

                # Check if the email belongs to a professor
                if email.endswith('.it@tip.edu.ph'):
                    return redirect('professor_dashboard')  # Redirect to professor's dashboard

                # Redirect regular users to the index page
                return redirect('index')
            else:
                return render(request, 'myapp/login.html', {'alert': 'Invalid email or password'})

        elif 'signup' in request.POST:
            # Handle signup
            name = request.POST.get('name')
            email = request.POST.get('email')
            password = request.POST.get('password')
            data_privacy_accepted = 'data_privacy' in request.POST

            if not email.endswith('@tip.edu.ph'):
                return render(request, 'myapp/login.html', {'alert': 'Email must end with @tip.edu.ph'})

            if User.objects.filter(username=email).exists():
                return render(request, 'myapp/login.html', {'alert': 'Email already exists'})

            user = User.objects.create_user(username=email, email=email, password=password)
            user.first_name = name
            user.is_active = False  # Deactivate account until it is confirmed
            user.save()

            # Create or update the UserProfile instance
            user_profile, created = UserProfile.objects.get_or_create(user=user)
            user_profile.accepted_data_privacy = data_privacy_accepted  # Set acceptance status
            user_profile.save()

            # Start a thread to delete the user after 2 minutes if not activated
            def delete_unactivated_user(user_id):
                threading.Timer(120, lambda: remove_user_if_inactive(user_id)).start()

            delete_unactivated_user(user.pk)

            # Generate activation link
            token = account_activation_token.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            domain ='127.0.0.1:8000'
            protocol = 'https' if request.is_secure() else 'http'
            link = f'{protocol}://{domain}/activate/{uid}/{token}/'

            # Send email
            subject = 'Activate Your Account'
            message = render_to_string('myapp/activation_email.html', {
                'user': user,
                'domain': domain,
                'link': link,
            })
            plain_message = strip_tags(message)
            send_mail(subject, plain_message, 'cyberclash.capstone@gmail.com', [email], html_message=message)

            return render(request, 'myapp/login.html', {'alert': 'Signup successful! Please check your email to activate your account'})

    # Handle GET request or POST without 'login' or 'signup' action
    return render(request, 'myapp/login.html')


def remove_user_if_inactive(user_id):
    try:
        user = User.objects.get(pk=user_id)
        if not user.is_active:  # If the user is still inactive
            user.delete()
            print(f"Deleted user with ID {user_id} due to inactivity.")
    except User.DoesNotExist:
        print(f"User with ID {user_id} does not exist or has already been activated.")

  
    

def activate(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        return redirect('loginPage')
    else:
        return render(request, 'myapp/activation_invalid.html')

def custom_logout(request):
    # Log out the user
    logout(request)
    
    # Clear the session data
    request.session.flush()  # This will remove all session data
    
    # Optionally, you can add a message
    
    # Redirect to the login page or homepage
    return redirect('index')



@csrf_exempt
def mark_all_as_read(request):
    if request.method == 'POST':
        EmailLog.objects.filter(is_new=True).update(is_new=False)
        new_email_count = EmailLog.objects.filter(is_new=True).count()
        return JsonResponse({'status': 'success', 'new_email_count': new_email_count})
    return JsonResponse({'status': 'error'}, status=400)

def feedback_view(request):
    if request.method == 'POST':
        feedback_text = request.POST.get('feedback')
        user = request.user if request.user.is_authenticated else None
        email = request.POST.get('email') if not user else user.email
        

        # Save the feedback
        Feedback.objects.create(user=user, email=email, feedback=feedback_text)

        # Add a success message
        return render(request, 'myapp/contact.html', {'alert': 'Feedback sent successfully!'})


    return render(request, 'myapp/contact.html')

def custom_404(request, exception=None):
    return render(request, '404.html', status=404)

def professor_manage_students(request):
    if not (request.user.is_superuser or request.user.email.endswith('.it@tip.edu.ph')):
        return redirect('index')  # Redirect to index if neither condition is met
    # Base queryset: exclude superusers and users with email ending in '.it@tip.edu.ph'
    users = User.objects.filter(is_superuser=False).exclude(email__endswith='.it@tip.edu.ph')

    # Extract filtering parameters from the request
    course = request.GET.get('course', '')
    program = request.GET.get('program', '')
    section = request.GET.get('section', '')

    # Apply filters dynamically
    if course:
        users = users.filter(userprofile__course=course)
    if program:
        users = users.filter(userprofile__program=program)
    if section:
        users = users.filter(userprofile__section=section)

    # Fetch distinct values for dropdown options
    courses = UserProfile.objects.values_list('course_code', flat=True).distinct()
    programs = UserProfile.objects.values_list('program', flat=True).distinct()
    sections = UserProfile.objects.values_list('section', flat=True).distinct()

    if request.method == 'POST':
        for user in users:
            first_name = request.POST.get(f'first_name_{user.id}')
            email = request.POST.get(f'email_{user.id}')
            user.first_name = first_name
            user.email = email
            user.username = email
            user.save()  # Save the updated user
        
        # Redirect to the same page to avoid resubmission
        return redirect('user_accounts')

    feedbacks = Feedback.objects.all()  # Fetch all feedback
    feedback_count = feedbacks.count()  # Get the count of feedback
    
    # Render the data to the template
    return render(request, 'myapp/professor/professor_manage_students.html', {
        'users': users,
        'courses': courses,
        'programs': programs,
        'sections': sections,
        'feedback_count': feedback_count,
        'feedbacks': feedbacks,
    })


from .models import Course

def add_course(request):
    if request.method == 'POST':
        course_code = request.POST.get('CourseCode')
        course_name = request.POST.get('CourseName')
        course_desc = request.POST.get('CourseDesc')
        program = request.POST.get('Program')
        section = request.POST.get('Section')

        # Save to the database, associating with the logged-in user
        Course.objects.create(
            CourseCode=course_code,
            CourseName=course_name,
            CourseDesc=course_desc,
            Program=program,
            Section=section,
            published_by=request.user,  # Associate the course with the logged-in user
        )

        # Add a success message
        messages.success(request, 'Course Published!')

        # Redirect to the same page (reload)
        return redirect('professor_sections')  # Ensure the URL name matches your configuration

    return render(request, 'myapp/professor/professor_sections.html')



from django.shortcuts import render
from django.contrib.auth.models import User
from .models import EmailLog
from django.db.models import Q

@login_required
def other_profiles(request):
    query = request.GET.get('q')
    
    # Get all users, excluding the logged-in user and superusers
    users = User.objects.exclude(id=request.user.id).exclude(is_superuser=True)

    # Exclude users with email ending in .it@tip.edu.ph
    users = users.exclude(email__endswith='.it@tip.edu.ph')

    # If a search query is provided, filter users based on username, first_name, or last_name
    if query:
        users = users.filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query)
        )
    # Annotate users with their total scores
    users = users.annotate(total_score=Sum('score__score')).order_by('-total_score')

    # Add ranks to each user
    for user in users:
        user.total_score = user.total_score or 0  # Handle users with no scores
        if user.total_score == 0:
            user.rank = "UNRANKED"
        elif 1 <= user.total_score <=200:
            user.rank = "BEGINNER"
        elif 201 <= user.total_score <= 400:
            user.rank = "INTERMEDIATE"
        elif 401 <= user.total_score <= 600:
            user.rank = "ADVANCED"
        elif 601 <= user.total_score <= 800:
            user.rank = "EXPERT"
        elif 801 <= user.total_score <= 100:
            user.rank = "PENETRATION TESTER"
        else:
            user.rank = "CERTIFIED ETHICAL HACKER"

    # Email count and logs for the logged-in user

    if request.user.is_authenticated:
        email_logs = EmailLog.objects.filter(recipients__icontains=request.user.email).order_by('-sent_at')
        email_count = email_logs.filter(is_new=True).count()
    else:
        email_logs = []
        email_count = 0
    user_role = "Student"  # Default role

    if request.user.is_superuser:
        user_role = "Admin"
    elif request.user.email.endswith('.it@tip.edu.ph'):
        user_role = "Professor"
    context = {
        'users': users,  # Pass the annotated users with scores and ranks
        'email_count': email_count,
        'email_logs': email_logs,
        'user_role':user_role,
        'query': query,  # Pass the search query to the template
    }

    return render(request, 'myapp/other_profiles.html', context)
from django.core.paginator import Paginator

def logs(request):
    if not request.user.is_superuser:
        return redirect('index')

    # Fetch all activity logs, ordered by the most recent first
    activity_logs = ActivityLog.objects.all().order_by('-created_at')

    # Set up pagination: 10 logs per page
    paginator = Paginator(activity_logs, 10)

    # Get the current page number from the request, default to 1
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'myapp/admin/logs.html', {'page_obj': page_obj})



from django.db.models import Sum, Count, Q

@login_required
def profile_view(request):
    if not request.user.is_authenticated:
        return redirect('index')  # Redirect to the index page if the user is not authenticated

    user = request.user

    # Perform the split pane analysis for the logged-in user
    analysis_status = student_analysis(user)  # Pass the logged-in user as an argument

    # Fetch the latest analysis
    analysis = StudentAnalysis.objects.filter(user=user).order_by('-created_at').first()
    textAnalytics = StudentAnalysis.objects.last()

    # Process the split graph analysis if it exists
    split_graph_sections = []
    if analysis and analysis.split_graph:
        split_graph_sections = analysis.split_graph.split("\n\n")

    user_score = (
        Score.objects.filter(user=user)  # Filter for the logged-in user
        .aggregate(total_score=Sum('score'))  # Calculate total score
    )
    total_score = user_score['total_score'] or 0  # Handle cases with no scores

    # Determine rank based on total score
    if total_score == 0:
        rank = "UNRANKED"
    elif 1 <= total_score <= 200:
        rank = "BEGINNER"
    elif 201 <= total_score <= 400:
        rank = "INTERMEDIATE"
    elif 401 <= total_score <= 600:
        rank = "PENETRATION TESTER"
    elif 601 <= total_score <= 800:
        rank = "CERTIFIED ETHICAL HACKER"
    elif 801 <= total_score <= 1000:
        rank = "CERTIFIED ETHICAL HACKER"
    else:
        rank = "CERTIFIED ETHICAL HACKER"

    # Exclude superuser and users with emails ending in '.it@tip.edu.ph'
    all_scores = (
        Score.objects.filter(user__is_superuser=False)  # Exclude superuser
        .exclude(user__email__endswith='.it@tip.edu.ph')  # Exclude specific email domain
        .values('user')  # Group by user
        .annotate(total_score=Sum('score'))  # Calculate total score per user
        .order_by('-total_score')  # Sort by total score descending
    )

    # Calculate rank number based on scores of all users
    rankno = next((index + 1 for index, score in enumerate(all_scores) if score['user'] == user.id), None)

    # Get email logs for the logged-in user
    email_logs = EmailLog.objects.filter(recipients__icontains=user.email).order_by('-sent_at')
    user_profile = request.user.userprofile
    # Count new emails for the logged-in user
    email_count = email_logs.filter(is_new=True).count()

    # Aggregate submission counts by category for the logged-in user
    category_submission_counts = Score.objects.filter(user=user) \
        .values('category') \
        .annotate(
            total_correct=Sum('correct_submissions'),
            total_incorrect=Sum('incorrect_submissions')
        )
    
    recent_activities = Score.objects.filter(user=request.user).order_by('-created_at')[:5]

    # Prepare data for performance, including dynamic percentages
    performance_data = []
    for entry in category_submission_counts:
        total = (entry['total_correct'] or 0) + (entry['total_incorrect'] or 0)
        performance_data.append({
            'category': entry['category'],
            'correct_ratio': round((entry['total_correct'] or 0) / total * 100, 2) if total > 0 else 0,
            'incorrect_ratio': round((entry['total_incorrect'] or 0) / total * 100, 2) if total > 0 else 0,
        })

    total_correct = sum(entry['total_correct'] or 0 for entry in category_submission_counts)
    total_attempts = sum(
        (entry['total_correct'] or 0) + (entry['total_incorrect'] or 0)
        for entry in category_submission_counts
    )
    performance_percentage = round((total_correct / total_attempts) * 100, 2) if total_attempts > 0 else 0

    # Get the user's most answered category
    user_canvas_states = Score.objects.filter(user=user).values('category')
    if user_canvas_states.exists():
        category_counts = Counter(state['category'] for state in user_canvas_states)  # Count each category
        top_category = category_counts.most_common(1)  # Get the most common category
        top_category_name = top_category[0][0] if top_category else "N/A"
    else:
        top_category_name = "N/A"  # No categories answered

    # Get courses to populate the dropdown
    courses = Course.objects.all()  # Assuming you have a Course model
    category_counts = (
    Score.objects.filter(user=user)
    .values('category')
    .annotate(count=Count('id'))  # Count the entries for each category
)
    recent_activities = Score.objects.filter(user=request.user).order_by('-created_at')[:5]

    # Add total_possible_score and total_possible_correct_answers to each activity
    for activity in recent_activities:
        # Calculate the total_possible_score and total_possible_correct_answers for each activity
        activity.total_possible_score = activity.total_possible_score  # This is directly from the model
        activity.total_possible_correct_answers = activity.total_possible_correct_answers
# Prepare data for the chart
    categories = [entry['category'] for entry in category_counts]  # Category names
    submission_counts = [entry['count'] for entry in category_counts]  # Counts per category
    user_role = "Student"  # Default role
    
    if request.user.is_superuser:
        user_role = "Admin"
    elif request.user.email.endswith('.it@tip.edu.ph'):
        user_role = "Professor"
    context = {
        'email_count': email_count,
        'email_logs': email_logs,
        'user_profile': user_profile,
        'categories': categories,
        'submission_counts': submission_counts,
        'total_score': total_score,
        'rank': rank,
        'analysis_status':analysis_status,
        'rankno': rankno or "Unranked",  # Handle case where rankno is None
        'performance_percentage': performance_percentage,
        'performance_data': performance_data,
        'top_category': top_category_name,
        'courses': courses,
        'recent_activities': recent_activities,
        'split_graph_sections': split_graph_sections,
        'analysis': analysis,
        'textAnalytics': textAnalytics,
        'user_role':user_role,
    }

    return render(request, 'myapp/profile.html', context)




@login_required
def profile_details(request, user_id):
    # Fetch the user profile of the selected user (not the logged-in user)
    user_profile = get_object_or_404(UserProfile, user__id=user_id)
    user = User.objects.get(id=user_id)  # Fetch user by user_id

    # Perform analysis for the selected user
    analysis_status = student_analysis(user_id)
    scores = Score.objects.filter(user__id=user_id)
    user_canvas_states = Score.objects.filter(user__id=user_id).values('category')
    
    # Fetch split graph data for the selected user
    analysis = StudentAnalysis.objects.filter(user__id=user_id).order_by('-created_at').first()
    split_graph_sections = []
    if analysis and analysis.split_graph:
        split_graph_sections = analysis.split_graph.split("\n\n")

    # Compute total score
    total_score = scores.aggregate(Sum('score'))['score__sum'] or 0

    # Determine the top answered category
    top_category = (
        scores.values('category')
        .annotate(category_count=Count('category'))
        .order_by('-category_count')
        .first()
    )

    recent_activities = Score.objects.filter(user__id=user_id).order_by('-created_at')[:5]

    # Compute performance percentage
    total_correct = scores.aggregate(Sum('correct_submissions'))['correct_submissions__sum'] or 0
    total_incorrect = scores.aggregate(Sum('incorrect_submissions'))['incorrect_submissions__sum'] or 0
    total_attempts = total_correct + total_incorrect
    performance_percent = (total_correct / total_attempts * 100) if total_attempts > 0 else 0

    # Get email logs for the selected user (not the logged-in user)
    email_logs = EmailLog.objects.filter(recipients__icontains=user.email).order_by('-sent_at')
    email_count = email_logs.filter(is_new=True).count()

    # Aggregate submission counts by category for the selected user
    category_submission_counts = Score.objects.filter(user=user) \
        .values('category') \
        .annotate(
            total_correct=Sum('correct_submissions'),
            total_incorrect=Sum('incorrect_submissions')
        )

    # Prepare data for performance, including dynamic percentages
    performance_data = [
        {
            'category': entry['category'],
            'correct_ratio': round((entry['total_correct'] or 0) / total * 100, 2) if (total := (entry['total_correct'] or 0) + (entry['total_incorrect'] or 0)) > 0 else 0,
            'incorrect_ratio': round((entry['total_incorrect'] or 0) / total * 100, 2) if total > 0 else 0,
        }
        for entry in category_submission_counts
    ]

    total_correct = sum(entry['total_correct'] or 0 for entry in category_submission_counts)
    total_attempts = sum(
        (entry['total_correct'] or 0) + (entry['total_incorrect'] or 0)
        for entry in category_submission_counts
    )
    performance_percentage = round((total_correct / total_attempts) * 100, 2) if total_attempts > 0 else 0

    # Assign ranks based on total_score
    if total_score == 0:
        rank = "UNRANKED"
    elif 1 <= total_score <= 200:
        rank = "BEGINNER"
    elif 201 <= total_score <= 400:
        rank = "INTERMEDIATE"
    elif 401 <= total_score <= 600:
        rank = "ADVANCED"
    elif 601 <= total_score <= 800:
        rank = "EXPERT"
    elif 801 <= total_score <= 1000:
        rank = "PENETRATION TESTER"
    else:
        rank = "CERTIFIED ETHICAL HACKER"

    # Filter out superusers and users with emails ending in .it@tip.edu.ph
    excluded_users = UserProfile.objects.filter(
        Q(user__is_superuser=True) | Q(user__email__iendswith=".it@tip.edu.ph")
    )

    all_scores = (
        Score.objects.filter(user__is_superuser=False)  # Exclude superuser
        .exclude(user__email__endswith='.it@tip.edu.ph')  # Exclude specific email domain
        .values('user')  # Group by user
        .annotate(total_score=Sum('score'))  # Calculate total score per user
        .order_by('-total_score')  # Sort by total score descending
    )

    # Calculate rank number based on scores of all users
    rankno = next((index + 1 for index, score in enumerate(all_scores) if score['user'] == user_id), None)
    category_counts = Counter(entry['category'] for entry in category_submission_counts)
    user_role = "Student"  # Default role

    if request.user.is_superuser:
        user_role = "Admin"
    elif request.user.email.endswith('.it@tip.edu.ph'):
        user_role = "Professor"
# Prepare the labels and counts for the pie chart
    category_labels = list(category_counts.keys())
    category_counts_values = list(category_counts.values())
    context = {
        'user_profile': user_profile,
        'scores': scores,
        'user_role':user_role,
        'total_score': total_score,
        'top_category': top_category['category'] if top_category else "N/A",
        'performance_percent': round(performance_percent, 2),
        'rank': rank,
        'analysis': analysis,
        'split_graph_sections': split_graph_sections,
        'rankno': rankno,  # Add rankno to context
        'recent_activities': recent_activities,
        'performance_percentage': performance_percentage,
        'category_labels': category_labels,  # Pass category labels
    'category_counts': category_counts_values, 
        'performance_data': performance_data,
    }

    return render(request, 'myapp/profile_details.html', context)


def professor_sections(request):
    if not (request.user.is_superuser or request.user.email.endswith('.it@tip.edu.ph')):
        return redirect('index')  # Redirect to index if neither condition is met
    
    # Filter courses based on the logged-in user
    courses = Course.objects.filter(published_by=request.user)
    
    context = {
        'courses': courses,
    }
    return render(request, 'myapp/professor/professor_sections.html', context)


def delete_course(request, course_id):
    if not (request.user.is_superuser or request.user.email.endswith('.it@tip.edu.ph')):
        return redirect('index')  # Redirect to index if neither condition is met

    try:
        course = Course.objects.get(id=course_id)
        course.delete()
        # Optionally, add a success message
    except Course.DoesNotExist:
        # Handle the case if the course doesn't exist
        pass

    messages.error(request, 'Course Deleted!')

        # Redirect to the same page (reload)
    return redirect('professor_sections')  # Ensure the URL name matches your configuration





from django.shortcuts import render
from .models import Score, UserProfile

def student_assessment(request):
    # Fetch all scores and related user profiles
    scores = Score.objects.select_related('user').all()
    user_profiles = UserProfile.objects.all()  # Get all user profiles
    challenges = CanvasState.objects.all()

    data = []
    for challenge in challenges:
        # Filter students who answered this challenge
        answered_students = [
            score for score in scores if score.canvas_state_title == challenge.title
        ]

        for score in answered_students:
            user_profile = user_profiles.filter(user_id=score.user_id).first()
            section = user_profile.section if user_profile else "N/A"

            canvas_state_title = score.canvas_state_title or "No Title"
            ratio = (
                f"{score.correct_submissions}/{score.total_possible_correct_answers}"
                if score.total_possible_correct_answers > 0
                else "N/A"
            )
            score_ratio = (
                f"{score.score}/{score.total_possible_score}"
                if score.total_possible_score > 0
                else "N/A"
            )
            canvas_explanation = score.canvas_explanation or "No explanation provided"

            data.append({
                "user": score.user.username,
                "canvas_state_title": canvas_state_title,
                "ratio": ratio,
                "score_ratio": score_ratio,
                "section": section,
                "canvas_explanation": canvas_explanation,
                "challenge_title": challenge.title
            })

    return render(request, 'myapp/professor/professor_answered.html', {
        "data": data,
        "challenges": challenges,
        "user_profiles": user_profiles
    })







@login_required
def upload_image(request):
    if request.method == 'POST' and 'profile_image' in request.FILES:
        user_profile = UserProfile.objects.get(user=request.user)
        user_profile.profile_image = request.FILES['profile_image']
        user_profile.save()
        return redirect('profile_view')
    return redirect('profile_view')
    
from django.contrib.auth.hashers import make_password
from django.contrib.auth import update_session_auth_hash

def update_profile(request):
    if request.method == "POST":
        # Handle updating the user profile
        user = request.user

        # Update the user's first name
        first_name = request.POST.get('first_name')
        if first_name:
            user.first_name = first_name

        # Update the password securely
        password = request.POST.get('password')
        repeat_password = request.POST.get('repeatPassword')

        if password and repeat_password:
            if password == repeat_password:
                # Set the new password
                user.password = make_password(password)
                user.save()

                # Update the session to keep the user logged in after password change
                update_session_auth_hash(request, user)
            else:
                # Handle password mismatch (optional: add flash message)
                return render(request, 'myapp/profile.html', {
                    'user': request.user,
                    'user_profile': UserProfile.objects.filter(user=request.user).first(),
                    'courses': Course.objects.all(),
                    'error': 'Passwords do not match'  # Optional error message
                })

        user.save()

        # Handle user profile updates
        try:
            user_profile = UserProfile.objects.get(user=user)
        except UserProfile.DoesNotExist:
            user_profile = UserProfile(user=user)

        # Get the section and program data from the POST request
        user_profile.section = request.POST.get('section')
        user_profile.program = request.POST.get('program')

        # Get the selected course (retrieve the course details from the database)
        course_id = request.POST.get('course')
        if course_id:
            try:
                # Fetch the Course object using the id
                course = Course.objects.get(id=course_id)
                # Store the CourseCode and CourseName in the UserProfile model
                user_profile.course_code = course.CourseCode
                user_profile.course_name = course.CourseName
            except Course.DoesNotExist:
                user_profile.course_code = None  # Ensure no course details if not found
                user_profile.course_name = None  # Ensure no course details if not found

        # Save the updated profile
        user_profile.save()

        return redirect('profile_view')  # Redirect to the profile page or another relevant page

    return render(request, 'myapp/profile.html', {
        'user': request.user,
        'user_profile': UserProfile.objects.filter(user=request.user).first(),
        'courses': Course.objects.all()  # Pass all available courses to the template
    })







@login_required
def admin_leaderboards(request):
    # Check if the user is a superuser
    if not request.user.is_superuser:
        return redirect('index')  # Redirect to a forbidden page or wherever you want

    # Fetch users excluding those with email ending in '.it@tip.edu.ph'
    users = User.objects.filter(is_superuser=False).exclude(email__endswith='.it@tip.edu.ph')
    # Calculate total scores for users and order by score in descending order (highest score first)
    user_scores = (
        Score.objects.values('user__id', 'user__first_name', 'user__email')
        .annotate(total_score=Sum('score'))  # Sum the scores for each user
        .order_by('-total_score')  # Sort by total score in descending order
    )

    # Assign ranks based on score order
    for idx, user_score in enumerate(user_scores, start=1):
        user_score['rank_no'] = idx  # Rank number, starting from 1
        if user_score['total_score'] == 0:
            user_score['rank'] = "UNRANKED"
        elif 1 <= user_score['total_score'] <= 200:
            user_score['rank'] = "BEGINNER"
        elif 201 <= user_score['total_score'] <= 400:
            user_score['rank'] = "INTERMEDIATE"
        elif 401 <= user_score['total_score'] <= 600:
            user_score['rank'] = "ADVANCED"
        elif 601 <= user_score['total_score'] <= 800:
            user_score['rank'] = "EXPERT"
        elif 801 <= user_score['total_score'] <= 1000:
            user_score['rank'] = "PENETRATION TESTER"
        else:
            user_score['rank'] = "CERTIFIED ETHICAL HACKER"


    if request.method == 'POST':
        for user in users:
            first_name = request.POST.get(f'first_name_{user.id}')
            email = request.POST.get(f'email_{user.id}')
            user.first_name = first_name
            user.email = email
            user.save()  # Save the updated user

        # Redirect to the same page to avoid resubmission
        return redirect('user_accounts')

    feedbacks = Feedback.objects.all()  # Fetch all feedback
    feedback_count = feedbacks.count()  # Get the count of feedback

    # Render the data to the template
    return render(request, 'myapp/admin/admin_leaderboards.html', {
        'user_scores': user_scores,
        'feedback_count': feedback_count,
        'feedbacks': feedbacks,
    })

@login_required
def professor_students(request):
    if not (request.user.is_superuser or request.user.email.endswith('.it@tip.edu.ph')):
        return redirect('index')  # Redirect to index if neither condition is met
    # Fetch users excluding those with email ending in '.it@tip.edu.ph'
    users = User.objects.filter(is_superuser=False).exclude(email__endswith='.it@tip.edu.ph')

    # Calculate total scores for users and order by score in descending order (highest score first)
    user_scores = (
        Score.objects.filter(user__is_superuser=False)
        .exclude(user__email__endswith='.it@tip.edu.ph')  # Exclude specific emails
        .values('user__id', 'user__first_name', 'user__email')
        .annotate(total_score=Sum('score'))  # Sum the scores for each user
        .order_by('-total_score')  # Sort by total score in descending order
    )

    # Assign ranks based on score order
    for idx, user_score in enumerate(user_scores, start=1):
        user_score['rank_no'] = idx  # Rank number, starting from 1
        if user_score['total_score'] == 0:
            user_score['rank'] = "UNRANKED"
        elif 1 <= user_score['total_score'] <= 200:
            user_score['rank'] = "BEGINNER"
        elif 201 <= user_score['total_score'] <= 400:
            user_score['rank'] = "INTERMEDIATE"
        elif 401 <= user_score['total_score'] <= 600:
            user_score['rank'] = "ADVANCED"
        elif 601 <= user_score['total_score'] <= 800:
            user_score['rank'] = "EXPERT"
        elif 801 <= user_score['total_score'] <= 1000:
            user_score['rank'] = "PENETRATION TESTER"
        else:
            user_score['rank'] = "CERTIFIED ETHICAL HACKER"

    if request.method == 'POST':
        for user in users:
            first_name = request.POST.get(f'first_name_{user.id}')
            email = request.POST.get(f'email_{user.id}')
            user.first_name = first_name
            user.email = email
            user.save()  # Save the updated user

        # Redirect to the same page to avoid resubmission
        return redirect('user_accounts')

    # Render the data to the template
    return render(request, 'myapp/professor/professor_students.html', {
        'user_scores': user_scores,
    })


@login_required
def user_accounts(request):
    # Check if the user is a superuser
    if not request.user.is_superuser:
        return redirect('index')  # Redirect to a forbidden page or wherever you want

    # Fetch users excluding those with email ending in '.it@tip.edu.ph'
    users = User.objects.filter(is_superuser=False).exclude(email__endswith='.it@tip.edu.ph')
    
    if request.method == 'POST':
        for user in users:
            first_name = request.POST.get(f'first_name_{user.id}')
            email = request.POST.get(f'email_{user.id}')
            
            # Ensure both first_name and email are provided
            if not first_name or not email:
                continue  # Skip if any required field is empty
            
            user.first_name = first_name
            user.email = email
            user.username = email  # Set the username to the email
            user.save()  # Save the updated user
            
        # Redirect to the same page to avoid resubmission
        return redirect('user_accounts')

    feedbacks = Feedback.objects.all()  # Fetch all feedback
    feedback_count = feedbacks.count()  # Get the count of feedback
    
    # Render the data to the template
    return render(request, 'myapp/admin/user_accounts.html', {
        'users': users,
        'feedback_count': feedback_count,
        'feedbacks': feedbacks,
    })

@login_required
def professor_accounts(request):
    # Check if the user is a superuser
    if not request.user.is_superuser:
        return redirect('index')  # Redirect to a forbidden page or wherever you want

    # Fetch users who are not superusers and include those with email ending in '.it@tip.edu.ph'
    users = User.objects.filter(is_superuser=False).filter(
        email__endswith='.it@tip.edu.ph'
    ).union(
        User.objects.filter(is_superuser=False).exclude(email__endswith='@tip.edu.ph')
    )

    if request.method == 'POST':
        for user in users:
            first_name = request.POST.get(f'first_name_{user.id}')
            email = request.POST.get(f'email_{user.id}')
            user.first_name = first_name
            user.email = email
            user.username = email
            user.save()  # Save the updated user

        # Redirect to the same page to avoid resubmission
        return redirect('professor_accounts')
    feedbacks = Feedback.objects.all()  # Fetch all feedback
    feedback_count = feedbacks.count()  # Get the count of feedback
    # Render the data to the template
    return render(request, 'myapp/admin/professor_accounts.html', {
        'users': users,
        'feedback_count':feedback_count,
        'feedbacks': feedbacks,
    })


@login_required
def user_feedbacks(request):
    # Check if the user is a superuser
    if not request.user.is_superuser:
        return redirect('index')  # Redirect to a forbidden page or wherever you want

    # Fetch all feedbacks
    feedbacks = Feedback.objects.all()
    feedback_count = feedbacks.count()

    # Render the data to the template
    return render(request, 'myapp/admin/user_feedbacks.html', {
        'feedbacks': feedbacks,
        'feedback_count': feedback_count,
    })

@login_required
def professor_dashboard(request):
    if not (request.user.is_superuser or request.user.email.endswith('.it@tip.edu.ph')):
        return redirect('index')  # Redirect to index if neither condition is met
    users = User.objects.filter(is_superuser=False)
    student_count = User.objects.filter(is_superuser=False).exclude(email__endswith='.it@tip.edu.ph').filter(email__endswith='@tip.edu.ph').count()
    student_status = User.objects.filter(userprofile__is_online=True, is_superuser=False).exclude(email__endswith='.it@tip.edu.ph').filter(email__endswith='@tip.edu.ph').count()
    professor_count = User.objects.filter(is_superuser=False, email__endswith='.it@tip.edu.ph').count()
    category_submission_counts = Score.objects.values('category') \
        .annotate(submission_count=Count('category')) \
        .order_by('category')
    challenges = CanvasState.objects.all()
    count_challenges = challenges.count()
    challengesdefend = CanvasStateDefend.objects.all()
    count_challengesdefend = challengesdefend.count()
    total_count = count_challenges + count_challengesdefend
    categories = [entry['category'] for entry in category_submission_counts]
    submission_counts = [entry['submission_count'] for entry in category_submission_counts]
    user_scores = Score.objects.values('user') \
        .annotate(total_score=Sum('score')) \
        .order_by('-total_score')
    users_names = [User.objects.get(id=entry['user']).username for entry in user_scores]
    total_scores = [entry['total_score'] for entry in user_scores]
    is_superuser = [user.is_superuser for user in users]
    data_for_analysis_pie = {
        "Submission Counts by Category": dict(zip(categories, submission_counts)),
    }
    data_for_analysis_bar = {
        "Users and Total Scores": dict(zip(users_names, total_scores)),
    }
    
    registrations_data = User.objects.annotate(
    registration_month=TruncMonth('date_joined')
    ).values('registration_month').annotate(
    student_count=Count('id', filter=Q(email__endswith='@tip.edu.ph') & ~Q(email__endswith='.it@tip.edu.ph')),
    professor_count=Count('id', filter=Q(email__endswith='.it@tip.edu.ph'))
    ).order_by('registration_month')
    registration_dates = [entry['registration_month'].strftime('%Y-%m-%d') if entry['registration_month'] else None for entry in registrations_data]
    student_registrations = [entry['student_count'] for entry in registrations_data]
    professor_registrations = [entry['professor_count'] for entry in registrations_data]
    area_chart_data = {
        "registration_dates": registration_dates,
        "student_registrations": student_registrations,
        "professor_registrations": professor_registrations,
    }
    split_pane_data = (
            Score.objects
            .values('category')
            .annotate(
                total_correct=Sum('correct_submissions'),
                total_incorrect=Sum('incorrect_submissions')
            )
        )
    split_graph_data = {
    entry['category']: {
        "total_correct": entry['total_correct'] or 0,  # Handle None values
        "total_incorrect": entry['total_incorrect'] or 0,  # Handle None values
    }
    for entry in split_pane_data
}
    area_analysis = generate_area_analysis(area_chart_data)
    data_for_analysis_area = {
        "Registrations Over Time": area_chart_data,
    }
    current_checksum = generate_data_checksum({
        "Pie Chart Data": data_for_analysis_pie,
        "Bar Chart Data": data_for_analysis_bar,
        "Area Chart Data": data_for_analysis_area,
        "Split Pane Data": split_graph_data,  # Include the new split graph data
    })
    latest_analysis = Analysis.objects.order_by('-created_at').first()
    if latest_analysis and latest_analysis.data_checksum == current_checksum:
        pie_analysis = latest_analysis.pie_graph
        bar_analysis = latest_analysis.bar_graph
        area_analysis = latest_analysis.areachart_graph if latest_analysis.areachart_graph else "Not Generated Yet"
        split_analysis = latest_analysis.split_graph or "Not Generated Yet"
    else:
        pie_analysis = generate_analysis(data_for_analysis_pie, 'pie_chart')
        bar_analysis = generate_analysis(data_for_analysis_bar, 'bar_chart')
        area_analysis = generate_analysis(data_for_analysis_area, 'area_chart')
        split_analysis = generate_analysis(split_graph_data, 'split_graph')

        Analysis.objects.create(
            pie_graph=pie_analysis,
            bar_graph=bar_analysis,
            areachart_graph=area_analysis,
            split_graph=split_analysis,
            data_checksum=current_checksum
        )
    category_submission_counts = Score.objects.values('category') \
        .annotate(
            total_correct=Sum('correct_submissions'),
            total_incorrect=Sum('incorrect_submissions')
        ) \
        .order_by('category')

    # Prepare the performance data for the template
    performance_data = []
    for entry in category_submission_counts:
        total = (entry['total_correct'] or 0) + (entry['total_incorrect'] or 0)
        performance_data.append({
            'category': entry['category'],
            'correct_ratio': round((entry['total_correct'] or 0) / total * 100, 2) if total > 0 else 0,
            'incorrect_ratio': round((entry['total_incorrect'] or 0) / total * 100, 2) if total > 0 else 0,
            'total_correct': entry['total_correct'] or 0,
            'total_incorrect': entry['total_incorrect'] or 0,
        })
    textAnalytics = Analysis.objects.last()
    top_challenge = Score.objects.values('canvas_state_title') \
                                 .annotate(total_count=Count('canvas_state_title')) \
                                 .order_by('-total_count') \
                                 .first()
    top_category = Score.objects.values('category') \
                                .annotate(total_count=Count('category')) \
                                .order_by('-total_count') \
                                .first()
    top_section = Score.objects.values('user__userprofile__section') \
                                    .annotate(total_count=Count('user__userprofile__section')) \
                                    .order_by('-total_count') \
                                    .first()
    return render(request, 'myapp/professor/professor_dashboard.html', {
        'users': users,
        'student_status': student_status,
        'student_count': student_count,
        'professor_count': professor_count,
        'categories': categories,
        'top_category': top_category,
        'submission_counts': submission_counts,
        'users_names': users_names,
        'total_count': total_count,
        'total_scores': total_scores,
        'is_superuser': is_superuser,
        'pie_analysis': pie_analysis,
        'bar_analysis': bar_analysis,
        'performance_data': performance_data,
        'top_challenge': top_challenge,
        'top_section': top_section,
        'area_analysis': area_analysis,
        'textAnalytics': textAnalytics,
        'analysis_created_at': textAnalytics.created_at if textAnalytics else None,   
    })

def email(request):
    if not request.user.is_superuser:
        return redirect('index') 

    # Exclude superusers from the queryset
    users = User.objects.exclude(is_superuser=True)
    feedbacks = Feedback.objects.all()  # Fetch all feedback
    
    # Check if 'recipient' is passed in the query string
    recipient_email = request.GET.get('recipient')

    # Add a success message if an email was sent or any action took place
    if 'email_sent' in request.GET:
        messages.success(request, 'Email sent successfully!')

    context = {
        'users': users,
        'feedbacks': feedbacks,
        'feedback_count': feedbacks.count(),
        'selected_recipient': recipient_email,  # Pass the recipient email to the template
    }
    
    return render(request, 'myapp/admin/email.html', context)



def send_email_view(request):
    if not request.user.is_superuser:
        return redirect('index') 
    if request.method == 'POST':
        recipients = request.POST.getlist('recipients')
        subject = request.POST.get('subject')
        body = request.POST.get('body')

        # Prepare email data
        if 'all' in recipients:
            # If 'all' is selected, get all user emails
            recipient_emails = [user.email for user in User.objects.all()]
        else:
            recipient_emails = recipients

        # Send email
        try:
            send_mail(
                subject,
                body,
                settings.EMAIL_HOST_USER,
                recipient_emails,
                fail_silently=False,
            )

            # Save email details to the database
            EmailLog.objects.create(
                recipients=', '.join(recipient_emails),
                subject=subject,
                body=body,
                sent_by=request.user if request.user.is_authenticated else None
            )

            messages.success(request, 'Email sent successfully!')
        except Exception as e:
            messages.error(request, f'Error sending email: {e}')
        
        return redirect('email')  # Redirect after successful send

    # Render your form template if not a POST request
    return render(request, 'myapp/admin/email.html')


def professor_announce_email(request):
    if not (request.user.is_superuser or request.user.email.endswith('.it@tip.edu.ph')):
        return redirect('index')  # Redirect to index if neither condition is met
    if request.method == 'POST':
        recipients = request.POST.getlist('recipients')
        subject = request.POST.get('subject')
        body = request.POST.get('body')

        # Prepare email data
        if 'all' in recipients:
            # If 'all' is selected, get all user emails
            recipient_emails = [user.email for user in User.objects.all()]
        else:
            recipient_emails = recipients

        # Send email
        try:
            send_mail(
                subject,
                body,
                settings.EMAIL_HOST_USER,
                recipient_emails,
                fail_silently=False,
            )

            # Save email details to the database
            EmailLog.objects.create(
                recipients=', '.join(recipient_emails),
                subject=subject,
                body=body,
                sent_by=request.user if request.user.is_authenticated else None
            )

            messages.success(request, 'Email sent successfully!')
        except Exception as e:
            messages.error(request, f'Error sending email: {e}')
        
        return redirect('professor_announce')  # Redirect after successful send

    # Render your form template if not a POST request
    return render(request, 'myapp/professor/professor_announce.html')



