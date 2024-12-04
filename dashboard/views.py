from datetime import timedelta

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import AlertForm, AQIForm, LocationForm, MetricForm
from .models import AirQualityIndex, Alert, Location, Metric
from .queries import SampleQueries
from .services.alert_service import AlertService
from .services.trend_service import TrendService

def index(request):
    latest_metrics = Metric.objects.select_related('location').order_by('-timestamp')[:5]
    locations = Location.objects.all()
    active_alerts = Alert.objects.filter(is_active=True)[:5]
    
    context = {
        'latest_metrics': latest_metrics,
        'locations': locations,
        'active_alerts': active_alerts,
    }
    return render(request, 'dashboard/index.html', context)

@login_required
def query_demonstration(request):
    """View to demonstrate all required queries"""

    join_results = SampleQueries.join_query_locations_with_alerts()
    aggregate_results = SampleQueries.aggregate_query_city_statistics()
    subquery_results = SampleQueries.subquery_high_pollution_locations()
    continuous_high_pollution_locations_results = SampleQueries.continuous_high_pollution_locations()
    temperature_spike_locations_results = SampleQueries.temperature_spike_locations()
    alerts_triggered_last_week_results = SampleQueries.alerts_triggered_last_week()

    context = {
        'join_results': join_results,
        'aggregate_results': aggregate_results,
        'subquery_results': subquery_results,
        'continuous_high_pollution_locations_results': continuous_high_pollution_locations_results,
        'temperature_spike_locations_results': temperature_spike_locations_results,
        'alerts_triggered_last_week_results': alerts_triggered_last_week_results,
        'queries_info': {
            'join_query': {
                'title': 'Join Query Example',
                'description': 'Demonstrates joining locations with metrics and alerts'
            },
            'aggregate_query': {
                'title': 'Aggregate Query Example',
                'description': 'Shows city statistics using GROUP BY and aggregate functions'
            },
            'subquery': {
                'title': 'Subquery Example',
                'description': 'Finds locations with above-average pollution levels'
            },
            'continuous_high_pollution_locations': {
                'title': 'Continuous High Pollution Locations',
                'description': 'Finds locations with continuous high pollution levels'
            },
            'temperature_spike_locations': {
                'title': 'Temperature Spike Locations',
                'description': 'Finds locations with temperature spikes'
            },
            'alerts_triggered_last_week': {
                'title': 'Alerts Triggered Last Week',
                'description': 'Finds alerts triggered in the last week'
            }
        }
    }
    return render(request, 'dashboard/query_demonstration.html', context)


# Location CRUD
@login_required
def location_list(request):
    locations = Location.objects.all().order_by('city')
    return render(request, 'dashboard/location_list.html', {'locations': locations})

@login_required
def location_detail(request, pk):
    location = get_object_or_404(Location, pk=pk)
    
    latest_metrics = Metric.objects.filter(
        location=location
    ).order_by('-timestamp')[:30]  # Last 30 readings
    
    aqi_history = AirQualityIndex.objects.filter(
        location=location
    ).order_by('-timestamp')[:30]
    
    alerts = Alert.objects.filter(
        location=location,
        is_active=True
    )
    
    if latest_metrics:

        df = pd.DataFrame(list(latest_metrics.values()))
        
        fig_pm25 = px.line(df, x='timestamp', y='pm25', 
                          title='PM2.5 Trend Over Time')
        pm25_graph = fig_pm25.to_html(full_html=False)
        
        fig_temp = px.line(df, x='timestamp', y=['temperature', 'humidity'],
                          title='Temperature and Humidity Trends')
        temp_humid_graph = fig_temp.to_html(full_html=False)
    else:
        pm25_graph = None
        temp_humid_graph = None

    metrics_list = list(latest_metrics)
    if metrics_list:
        avg_temp = sum(m.temperature for m in metrics_list if m.temperature) / len(metrics_list)
        avg_humidity = sum(m.humidity for m in metrics_list if m.humidity) / len(metrics_list)
    else:
        avg_temp = 0
        avg_humidity = 0
    
    context = {
        'location': location,
        'latest_metrics': latest_metrics,
        'aqi_history': aqi_history,
        'alerts': alerts,
        'pm25_graph': pm25_graph,
        'avg_temp': avg_temp,
        'avg_humidity': avg_humidity,
        'temp_humid_graph': temp_humid_graph
    }
    return render(request, 'dashboard/location_detail.html', context)

@login_required
def location_create(request):
    if request.method == 'POST':
        form = LocationForm(request.POST)
        if form.is_valid():
            location = form.save()
            messages.success(request, 'Location created successfully!')
            return redirect('location_detail', pk=location.pk)
    else:
        form = LocationForm()
    return render(request, 'dashboard/location_form.html', {'form': form, 'action': 'Create'})

@login_required
def location_update(request, pk):
    location = get_object_or_404(Location, pk=pk)
    if request.method == 'POST':
        form = LocationForm(request.POST, instance=location)
        if form.is_valid():
            location = form.save()
            messages.success(request, 'Location updated successfully!')
            return redirect('location_detail', pk=location.pk)
    else:
        form = LocationForm(instance=location)
    return render(request, 'dashboard/location_form.html', {'form': form, 'action': 'Update'})

@login_required
def location_delete(request, pk):
    location = get_object_or_404(Location, pk=pk)
    if request.method == 'POST':
        location.delete()
        messages.success(request, 'Location deleted successfully!')
        return redirect('location_list')
    return render(request, 'dashboard/location_confirm_delete.html', {'location': location})

# Metric CRUD
@login_required
def metric_list(request):
    metrics = Metric.objects.all().order_by('-timestamp')
    return render(request, 'dashboard/metric_list.html', {'metrics': metrics})

@login_required
def metric_detail(request, pk):
    metric = get_object_or_404(Metric, pk=pk)
    
    # Get surrounding metrics for context (5 before and 5 after)
    surrounding_metrics = Metric.objects.filter(
        location=metric.location,
        timestamp__range=[
            metric.timestamp - timedelta(hours=5),
            metric.timestamp + timedelta(hours=5)
        ]
    ).order_by('timestamp')

    # Get AQI data for the same timeframe
    aqi_data = AirQualityIndex.objects.filter(
        location=metric.location,
        timestamp__range=[
            metric.timestamp - timedelta(hours=5),
            metric.timestamp + timedelta(hours=5)
        ]
    ).first()

    # Create visualization of all metrics
    if surrounding_metrics:
        df = pd.DataFrame(list(surrounding_metrics.values()))
        
        # Create multi-parameter plot
        fig = px.line(df, x='timestamp', 
                     y=['pm25', 'pm10', 'o3', 'no2', 'so2'],
                     title='Air Quality Parameters Over Time')
        parameters_graph = fig.to_html(full_html=False)

        # Create temperature and humidity plot
        fig_temp = px.line(df, x='timestamp', 
                          y=['temperature', 'humidity'],
                          title='Temperature and Humidity')
        temp_humid_graph = fig_temp.to_html(full_html=False)
    else:
        parameters_graph = None
        temp_humid_graph = None

    context = {
        'metric': metric,
        'surrounding_metrics': surrounding_metrics,
        'aqi_data': aqi_data,
        'parameters_graph': parameters_graph,
        'temp_humid_graph': temp_humid_graph,
    }
    return render(request, 'dashboard/metric_detail.html', context)

@login_required
def metric_create(request):
    if request.method == 'POST':
        form = MetricForm(request.POST)
        if form.is_valid():
            metric = form.save()
            messages.success(request, 'Metric created successfully!')
            return redirect('metric_detail', pk=metric.pk)
    else:
        form = MetricForm()
    return render(request, 'dashboard/metric_form.html', {'form': form, 'action': 'Create'})

@login_required
def metric_update(request, pk):
    metric = get_object_or_404(Metric, pk=pk)
    if request.method == 'POST':
        form = MetricForm(request.POST, instance=metric)
        if form.is_valid():
            metric = form.save()
            messages.success(request, 'Metric updated successfully!')
            return redirect('metric_detail', pk=metric.pk)
    else:
        form = MetricForm(instance=metric)
    return render(request, 'dashboard/metric_form.html', {'form': form, 'action': 'Update'})

@login_required
def metric_delete(request, pk):
    metric = get_object_or_404(Metric, pk=pk)
    if request.method == 'POST':
        metric.delete()
        messages.success(request, 'Metric deleted successfully!')
        return redirect('metric_list')
    return render(request, 'dashboard/metric_confirm_delete.html', {'metric': metric})

# Alert CRUD
@login_required
def alert_list(request):
    alerts = Alert.objects.filter(user=request.user).select_related('location').order_by('-created_at')
    return render(request, 'dashboard/alert_list.html', {'alerts': alerts})

@login_required
def alert_detail(request, pk):
    alert = get_object_or_404(Alert, pk=pk)
    
    # Get metrics related to this alert's threshold
    relevant_metrics = Metric.objects.filter(
        location=alert.location,
        timestamp__gte=timezone.now() - timedelta(days=7)
    ).order_by('-timestamp')
    
    # Create visualization of metric vs threshold
    if relevant_metrics:
        df = pd.DataFrame(list(relevant_metrics.values()))
        metric_field = alert.metric_type.lower().replace('.', '')
        
        fig = px.line(df, x='timestamp', y=metric_field,
                     title=f'{alert.metric_type} Values vs Alert Threshold')
        fig.add_hline(y=float(alert.threshold_value), 
                     line_dash="dash", 
                     line_color="red",
                     annotation_text="Threshold")
        threshold_graph = fig.to_html(full_html=False)
    else:
        threshold_graph = None
    
    context = {
        'alert': alert,
        'relevant_metrics': relevant_metrics[:10],  # Last 10 readings
        'threshold_graph': threshold_graph
    }
    return render(request, 'dashboard/alert_detail.html', context)

@login_required
def alert_create(request):
    if request.method == 'POST':
        form = AlertForm(request.POST)
        if form.is_valid():
            # Instead of directly saving, use the service
            alert, violations = AlertService.create_alert_with_check(
                user=request.user,
                location=form.cleaned_data['location'],
                metric_type=form.cleaned_data['metric_type'],
                threshold_value=form.cleaned_data['threshold_value']
            )

            if violations:
                messages.warning(
                    request,
                    f'Alert created, but there are {len(violations)} violations in the last 24 hours!'
                )
                return redirect('alert_violations', alert_id=alert.id)
            else:
                messages.success(request, 'Alert created successfully!')
                return redirect('alert_list')
    else:
        form = AlertForm()
    
    return render(request, 'dashboard/alert_form.html', {
        'form': form,
        'action': 'Create'
    })

@login_required
def alert_violations(request, alert_id):
    alert = get_object_or_404(Alert, id=alert_id, user=request.user)
    
    _, violations = AlertService.create_alert_with_check(
        user=alert.user,
        location=alert.location,
        metric_type=alert.metric_type,
        threshold_value=alert.threshold_value
    )

    return render(request, 'dashboard/alert_violations.html', {
        'alert': alert,
        'violations': violations
    })

@login_required
def check_alert_violations(request):
    alerts = Alert.objects.filter(
        user=request.user,
        is_active=True
    ).select_related('location')

    violations = []
    for alert in alerts:
        latest_metric = Metric.objects.filter(
            location=alert.location
        ).order_by('-timestamp').first()

        if latest_metric:
            current_value = getattr(latest_metric, alert.metric_type.lower().replace('.', ''), None)
            
            if current_value and current_value > alert.threshold_value:
                violations.append({
                    'alert': alert,
                    'current_value': current_value,
                    'threshold': alert.threshold_value,
                    'timestamp': latest_metric.timestamp,
                    'excess': current_value - alert.threshold_value
                })

    return render(request, 'dashboard/alert_violations_check.html', {
        'violations': violations
    })


@login_required
def alert_update(request, pk):
    alert = get_object_or_404(Alert, pk=pk)
    if request.method == 'POST':
        form = AlertForm(request.POST, instance=alert)
        if form.is_valid():
            alert = form.save()
            messages.success(request, 'Alert updated successfully!')
            return redirect('alert_list')
    else:
        form = AlertForm(instance=alert)
    return render(request, 'dashboard/alert_form.html', {'form': form, 'action': 'Update'})

@login_required
def alert_delete(request, pk):
    alert = get_object_or_404(Alert, pk=pk)
    if request.method == 'POST':
        alert.delete()
        messages.success(request, 'Alert deleted successfully!')
        return redirect('alert_list')
    return render(request, 'dashboard/alert_confirm_delete.html', {'alert': alert})

# AQI CRUD
@login_required
def aqi_list(request):
    aqi_records = AirQualityIndex.objects.all().order_by('-timestamp')
    return render(request, 'dashboard/aqi_list.html', {'aqi_records': aqi_records})

@login_required
def aqi_detail(request, pk):
    aqi = get_object_or_404(AirQualityIndex, pk=pk)
    
    # Get historical AQI data for this location
    historical_aqi = AirQualityIndex.objects.filter(
        location=aqi.location
    ).order_by('-timestamp')[:30]  # Last 30 readings
    
    # Create AQI trend visualization
    if historical_aqi:
        df = pd.DataFrame(list(historical_aqi.values()))
        
        fig = px.line(df, x='timestamp', y='aqi_value',
                     title='AQI Trend Over Time')
        # Add colored regions for AQI categories
        fig.add_hrect(y0=0, y1=50, fillcolor="green", opacity=0.1, line_width=0)
        fig.add_hrect(y0=51, y1=100, fillcolor="yellow", opacity=0.1, line_width=0)
        fig.add_hrect(y0=101, y1=150, fillcolor="orange", opacity=0.1, line_width=0)
        fig.add_hrect(y0=151, y1=200, fillcolor="red", opacity=0.1, line_width=0)
        fig.add_hrect(y0=201, y1=300, fillcolor="purple", opacity=0.1, line_width=0)
        fig.add_hrect(y0=301, y1=500, fillcolor="maroon", opacity=0.1, line_width=0)
        
        aqi_graph = fig.to_html(full_html=False)
    else:
        aqi_graph = None
    
    context = {
        'aqi': aqi,
        'historical_aqi': historical_aqi,
        'aqi_graph': aqi_graph
    }
    return render(request, 'dashboard/aqi_detail.html', context)

@login_required
def aqi_create(request):
    if request.method == 'POST':
        form = AQIForm(request.POST)
        if form.is_valid():
            aqi = form.save()
            messages.success(request, 'AQI record created successfully!')
            return redirect('aqi_detail', pk=aqi.pk)
    else:
        form = AQIForm()
    return render(request, 'dashboard/aqi_form.html', {'form': form, 'action': 'Create'})

@login_required
def aqi_update(request, pk):
    aqi = get_object_or_404(AirQualityIndex, pk=pk)
    if request.method == 'POST':
        form = AQIForm(request.POST, instance=aqi)
        if form.is_valid():
            aqi = form.save()
            messages.success(request, 'AQI record updated successfully!')
            return redirect('aqi_detail', pk=aqi.pk)
    else:
        form = AQIForm(instance=aqi)
    return render(request, 'dashboard/aqi_form.html', {'form': form, 'action': 'Update'})

@login_required
def aqi_delete(request, pk):
    aqi = get_object_or_404(AirQualityIndex, pk=pk)
    if request.method == 'POST':
        aqi.delete()
        messages.success(request, 'AQI record deleted successfully!')
        return redirect('aqi_list')
    return render(request, 'dashboard/aqi_confirm_delete.html', {'aqi': aqi})


@login_required
def location_trends(request, location_id):
    location = get_object_or_404(Location, pk=location_id)
    
    # Get period from query params or default to 30 days
    days = int(request.GET.get('days', 30))
    
    # Generate trends if needed
    TrendService.generate_trends(location, days)
    
    # Get trend summary
    trend_summary = TrendService.get_trend_summary(location, days)
    
    # Create visualizations using plotly
    graphs = {}
    for metric_type, data in trend_summary.items():
        if data['dates']:  # Only create graph if we have data
            fig = go.Figure()
            
            # Add average line
            fig.add_trace(go.Scatter(
                x=data['dates'],
                y=data['avg_values'],
                name='Average',
                line=dict(color='blue')
            ))
            
            # Add range
            fig.add_trace(go.Scatter(
                x=data['dates'] + data['dates'][::-1],
                y=data['max_values'] + data['min_values'][::-1],
                fill='toself',
                fillcolor='rgba(0,0,255,0.1)',
                line=dict(color='rgba(255,255,255,0)'),
                name='Range',
                showlegend=False
            ))
            
            fig.update_layout(
                title=f'{metric_type} Trends',
                xaxis_title='Date',
                yaxis_title='Value',
                height=400,
                margin=dict(l=20, r=20, t=40, b=20)
            )
            
            graphs[metric_type] = fig.to_html(full_html=False)
    
    context = {
        'location': location,
        'graphs': graphs,
        'days': days,
        'trend_summary': trend_summary
    }
    
    return render(request, 'dashboard/location_trends.html', context)