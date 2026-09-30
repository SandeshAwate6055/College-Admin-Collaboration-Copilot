import csv
import os
import random
from datetime import date, timedelta

random.seed(42)

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "csv")
os.makedirs(OUTPUT_DIR, exist_ok=True)

FIRST_NAMES = [
    "Aarav", "Aditya", "Rohan", "Siddharth", "Pranav", "Atharva", "Omkar", "Yash", "Suyash", "Shubham",
    "Abhishek", "Varun", "Tejas", "Tanmay", "Kunal", "Harsh", "Prathamesh", "Chinmay", "Gaurav", "Sanket",
    "Ananya", "Sneha", "Tanvi", "Pooja", "Riya", "Shruti", "Isha", "Neha", "Sayali", "Mrunal",
    "Aditi", "Sakshi", "Vaishnavi", "Radhika", "Gauri", "Shreya", "Kavya", "Akanksha", "Bhakti", "Manasi"
]

LAST_NAMES = [
    "Patil", "Deshmukh", "Kulkarni", "Joshi", "Shinde", "Pawar", "Chavan", "Kadam", "More", "Gaikwad",
    "Bhosale", "Jadhav", "Sutar", "Sawant", "Wagh", "Tambe", "Mane", "Ingale", "Shetty", "Iyer",
    "Nair", "Sharma", "Verma", "Gupta", "Mehta", "Shah", "Agarwal", "Bansal", "Chopra", "Malhotra"
]

BRANCHES = [
    ("Computer Engineering", "CS"),
    ("Information Technology", "IT"),
    ("Artificial Intelligence & Data Science", "AIDS"),
    ("Electronics & Telecommunication", "E&TC"),
    ("Mechanical Engineering", "MECH"),
    ("Chemical Engineering", "CHEM"),
    ("Instrumentation Engineering", "INSTRU")
]

YEAR_BATCH_MAP = [
    ("BTECH", 2021, "1211"),
    ("TY", 2022, "1221"),
    ("SY", 2023, "1231"),
    ("FY", 2024, "1241")
]

DOMAINS_BY_BRANCH = {
    "CS": ["Computer Vision", "Natural Language Processing", "Cloud Computing", "Full Stack Web Development", "Cybersecurity", "Blockchain", "DevOps"],
    "IT": ["Cloud Architecture", "Distributed Systems", "Web Engineering", "Information Security", "Microservices", "Big Data Analytics"],
    "AIDS": ["Deep Learning", "Generative AI", "Predictive Analytics", "Computer Vision", "NLP & LLMs", "Reinforcement Learning"],
    "E&TC": ["Embedded Systems", "IoT & Sensor Networks", "VLSI Design", "Signal Processing", "Wireless Communication", "Edge AI"],
    "MECH": ["Robotics & Automation", "Electric Vehicles (EV)", "CAD/CAM & FEA", "Thermal Engineering", "Mechatronics"],
    "CHEM": ["Process Automation", "Green Energy & Biofuels", "Computational Fluid Dynamics", "Polymer Technology", "Water Treatment Systems"],
    "INSTRU": ["Industrial Automation (PLC/SCADA)", "Biomedical Instrumentation", "Process Control Systems", "Smart Sensors & IoT"]
}

TECH_BY_DOMAIN = {
    "Computer Vision": ["Python", "OpenCV", "PyTorch", "YOLOv8", "TensorFlow"],
    "Natural Language Processing": ["Python", "HuggingFace", "Transformers", "BERT", "SpaCy"],
    "NLP & LLMs": ["Python", "LangChain", "Groq API", "LlamaIndex", "Vector DBs"],
    "Deep Learning": ["Python", "PyTorch", "Keras", "CUDA", "FastAPI"],
    "Generative AI": ["Python", "OpenAI API", "Diffusion Models", "RAG Pipeline", "Streamlit"],
    "Predictive Analytics": ["Python", "Pandas", "Scikit-Learn", "XGBoost", "PowerBI"],
    "Cloud Computing": ["AWS", "Docker", "Kubernetes", "Terraform", "Linux"],
    "Cloud Architecture": ["AWS", "Azure", "GCP", "Docker", "Microservices"],
    "Full Stack Web Development": ["React.js", "Node.js", "PostgreSQL", "TailwindCSS", "Next.js"],
    "Web Engineering": ["TypeScript", "React.js", "Express.js", "MongoDB", "GraphQL"],
    "Cybersecurity": ["Wireshark", "Kali Linux", "Metasploit", "Cryptography", "Network Security"],
    "Information Security": ["OWASP ZAP", "Burp Suite", "SIEM", "Penetration Testing", "Python"],
    "Blockchain": ["Solidity", "Ethereum", "Smart Contracts", "Hardhat", "Web3.js"],
    "DevOps": ["Docker", "Kubernetes", "Jenkins", "GitHub Actions", "Terraform"],
    "Distributed Systems": ["Go", "gRPC", "Kafka", "Redis", "Docker"],
    "Big Data Analytics": ["Apache Spark", "Hadoop", "PySpark", "Kafka", "SQL"],
    "Embedded Systems": ["Embedded C", "ARM Cortex", "STM32", "FreeRTOS", "UART/SPI/I2C"],
    "IoT & Sensor Networks": ["ESP32", "Arduino", "MQTT", "Node-RED", "Raspberry Pi"],
    "VLSI Design": ["Verilog", "VHDL", "Cadence", "Xilinx Vivado", "FPGA"],
    "Signal Processing": ["MATLAB", "Simulink", "Python", "Digital Filters", "DSP Processors"],
    "Wireless Communication": ["5G NR", "Software Defined Radio", "GNSS", "Zigbee", "MATLAB"],
    "Edge AI": ["TensorFlow Lite", "Jetson Nano", "OpenVINO", "Edge TPU", "Python"],
    "Robotics & Automation": ["ROS2", "Gazebo", "Python", "C++", "Kinematics & SLAM"],
    "Electric Vehicles (EV)": ["Battery Management Systems (BMS)", "MATLAB/Simulink", "Motor Control", "CAN Bus"],
    "CAD/CAM & FEA": ["SolidWorks", "ANSYS Workbench", "AutoCAD", "Finite Element Analysis"],
    "Thermal Engineering": ["ANSYS Fluent", "CFD", "Heat Transfer Modeling", "Thermal Imaging"],
    "Mechatronics": ["Arduino", "Actuators & Sensors", "Pneumatics", "PLC", "Python"],
    "Process Automation": ["SCADA", "Honeywell DCS", "MATLAB", "Aspen Plus"],
    "Green Energy & Biofuels": ["Chemical Process Simulation", "Bioreactors", "Gas Chromatography"],
    "Computational Fluid Dynamics": ["ANSYS Fluent", "OpenFOAM", "Mesh Generation", "Linux"],
    "Polymer Technology": ["Polymer Rheology", "Injection Molding Simulation", "Material Testing"],
    "Water Treatment Systems": ["Membrane Filtration Modeling", "Industrial Effluent Analysis", "Process Design"],
    "Industrial Automation (PLC/SCADA)": ["Siemens TIA Portal", "Allen Bradley PLC", "Wonderware SCADA", "Modbus"],
    "Biomedical Instrumentation": ["LabVIEW", "Bio-Sensors", "ECG/EEG Signal Processing", "MATLAB"],
    "Process Control Systems": ["PID Tuning", "Distributed Control Systems", "MATLAB", "Fieldbus Protocols"],
    "Smart Sensors & IoT": ["Smart Transducers", "IO-Link", "MQTT", "Python", "MicroPython"]
}

COMPANIES = [
    ("Persistent Systems", "Pune"),
    ("Barclays", "Pune"),
    ("Veritas Technologies", "Pune"),
    ("Nvidia", "Pune / Bangalore"),
    ("Eaton Corporation", "Pune"),
    ("Cummins India", "Pune"),
    ("Tata Consultancy Services", "Pune"),
    ("Infosys", "Pune"),
    ("Cognizant", "Pune"),
    ("Mastercard", "Pune"),
    ("Deutsche Bank", "Pune"),
    ("Bajaj Auto", "Pune"),
    ("Thermax", "Pune"),
    ("Siemens", "Pune"),
    ("Tata Technologies", "Pune"),
    ("L&T Technology Services", "Pune"),
    ("Rakuten", "Bangalore"),
    ("PhonePe", "Bangalore"),
    ("Accenture", "Pune"),
    ("Tech Mahindra", "Pune")
]

HACKATHONS = [
    ("Smart India Hackathon (SIH)", "National"),
    ("HackVIT Pune", "College"),
    ("MindSpark Pune", "State"),
    ("Melange Innovation Challenge", "College"),
    ("Flipkart GRiD", "National"),
    ("Kavach Cybersecurity Hackathon", "National"),
    ("Barclays Hackathon", "Corporate"),
    ("Tata Crucible Hackathon", "National"),
    ("Hackerearth AI Challenge", "National"),
    ("ACM-ICPC Regional Prelims", "National")
]

PLATFORMS = ["NPTEL", "Coursera", "AWS Academy", "Google Cloud Skills Boost", "edX", "Cisco Networking Academy"]

JOURNALS_AND_CONFERENCES = [
    ("IEEE International Conference on Computing, Communication and Control (ICCCI)", "Conference"),
    ("IEEE International Conference on Computing Communication Control and automation (ICCUBEA)", "Conference"),
    ("Springer Lecture Notes in Electrical Engineering", "Conference"),
    ("Elsevier Procedia Computer Science", "Journal"),
    ("IEEE Access", "Journal"),
    ("Springer Journal of Real-Time Image Processing", "Journal"),
    ("International Journal of Intelligent Systems", "Journal"),
    ("Taylor & Francis - Computer Science and Information Systems", "Journal")
]

print("Generating 1000 VIT students and their relational profiles...")

students = []
used_prns = set()

for i in range(1, 1001):
    first_name = random.choice(FIRST_NAMES)
    last_name = random.choice(LAST_NAMES)
    student_name = f"{first_name} {last_name}"
    
    branch_name, branch_code = random.choice(BRANCHES)
    year, batch_year, prefix = random.choice(YEAR_BATCH_MAP)
    
    # Generate unique PRN
    prn_num = random.randint(100, 999)
    prn = f"{prefix}{random.randint(10,99)}{prn_num:03d}"
    while prn in used_prns:
        prn_num = random.randint(100, 999)
        prn = f"{prefix}{random.randint(10,99)}{prn_num:03d}"
    used_prns.add(prn)

    roll_no = f"{branch_code}-{year}-{i % 120 + 1:03d}"
    cgpa = round(random.uniform(6.8, 9.85), 2)
    email = f"{first_name.lower()}.{last_name.lower()}{i % 50 if i > 100 else ''}@vit.edu"
    
    domains = DOMAINS_BY_BRANCH[branch_code]
    primary_domain = random.choice(domains)
    tech_stack = TECH_BY_DOMAIN.get(primary_domain, ["Python", "C++", "Linux"])
    
    students.append({
        "student_name": student_name,
        "PRN_or_Roll_No": prn,
        "roll_no": roll_no,
        "branch": branch_name,
        "branch_code": branch_code,
        "year": year,
        "cgpa": cgpa,
        "email": email,
        "primary_domain": primary_domain,
        "technologies": ", ".join(tech_stack)
    })

# 1. Master Students CSV
with open(os.path.join(OUTPUT_DIR, "students_master.csv"), "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=[
        "student_name", "PRN_or_Roll_No", "roll_no", "branch", "branch_code", "year", "cgpa", "email", "primary_domain", "technologies"
    ])
    writer.writeheader()
    writer.writerows(students)

# 2. Industry Projects CSV
industry_projects = []
for s in students:
    if s["year"] in ("TY", "BTECH") or random.random() < 0.35:
        company, _ = random.choice(COMPANIES)
        title = f"{s['primary_domain']} System for {company.split()[0]} Operations"
        start_date = f"2025-0{random.randint(1, 4)}-15"
        end_date = f"2025-0{random.randint(5, 9)}-30"
        industry_projects.append({
            "Student_Name": s["student_name"],
            "PRN_or_Roll_No": s["PRN_or_Roll_No"],
            "Branch": s["branch"],
            "Year": s["year"],
            "Company_Name": company,
            "Project_Title": title,
            "Project_Domain": s["primary_domain"],
            "Project_Start_Date": start_date,
            "Project_End_Date": end_date
        })

with open(os.path.join(OUTPUT_DIR, "industry_projects.csv"), "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=[
        "Student_Name", "PRN_or_Roll_No", "Branch", "Year", "Company_Name", "Project_Title", "Project_Domain", "Project_Start_Date", "Project_End_Date"
    ])
    writer.writeheader()
    writer.writerows(industry_projects)

# 3. Academic Projects CSV
academic_projects = []
categories = ["Capstone Project", "Engineering Design Project (EDP)", "Course Project", "Mini Project"]
for s in students:
    num_proj = random.randint(1, 2)
    for k in range(num_proj):
        cat = "Capstone Project" if s["year"] == "BTECH" else random.choice(categories[1:])
        title = f"Design and Implementation of {s['primary_domain']} using {s['technologies'].split(',')[0]}"
        academic_projects.append({
            "Student_Name": s["student_name"],
            "PRN_or_Roll_No": s["PRN_or_Roll_No"],
            "Branch": s["branch"],
            "Year": s["year"],
            "Project_Title": title,
            "Project_Category": cat,
            "Project_Domain": s["primary_domain"],
            "Project_Status": "Completed" if s["year"] in ("TY", "BTECH") else random.choice(["Completed", "Ongoing"])
        })

with open(os.path.join(OUTPUT_DIR, "academic_projects.csv"), "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=[
        "Student_Name", "PRN_or_Roll_No", "Branch", "Year", "Project_Title", "Project_Category", "Project_Domain", "Project_Status"
    ])
    writer.writeheader()
    writer.writerows(academic_projects)

# 4. Internships CSV
internships = []
roles_by_branch = {
    "CS": ["Software Engineer Intern", "Backend Developer Intern", "AI/ML Intern", "Cloud Engineering Intern"],
    "IT": ["Full Stack Intern", "Cloud DevOps Intern", "Data Analyst Intern", "Cybersecurity Intern"],
    "AIDS": ["Machine Learning Intern", "Data Science Intern", "AI Research Intern", "Computer Vision Intern"],
    "E&TC": ["Embedded Systems Intern", "IoT Firmware Intern", "Hardware Design Intern", "Wireless Protocol Intern"],
    "MECH": ["Robotics Design Intern", "CAE Simulation Intern", "EV Powertrain Intern", "CAD Modeling Intern"],
    "CHEM": ["Process Engineering Intern", "Chemical Analyst Intern", "Biofuel Research Intern"],
    "INSTRU": ["Automation Intern", "PLC Programmer Intern", "Instrumentation Trainee"]
}

for s in students:
    # 70% of TY/BTECH and 30% of SY have internships
    if (s["year"] in ("TY", "BTECH") and random.random() < 0.8) or (s["year"] == "SY" and random.random() < 0.35):
        company, _ = random.choice(COMPANIES)
        role = random.choice(roles_by_branch.get(s["branch_code"], ["Engineering Intern"]))
        mode = random.choice(["Offline (On-site)", "Hybrid", "Remote (Online)"])
        stipend = random.choice(["₹15,000 / month", "₹20,000 / month", "₹25,000 / month", "₹30,000 / month", "₹40,000 / month", "₹50,000 / month"])
        internships.append({
            "Student_Name": s["student_name"],
            "PRN_or_Roll_No": s["PRN_or_Roll_No"],
            "Branch": s["branch"],
            "Year": s["year"],
            "Internship_Company_Name": company,
            "Internship_Role": role,
            "Internship_Mode": mode,
            "Internship_Start_Date": "2025-06-01",
            "Internship_End_Date": "2025-08-31",
            "Stipend_Amount": stipend
        })

with open(os.path.join(OUTPUT_DIR, "internships.csv"), "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=[
        "Student_Name", "PRN_or_Roll_No", "Branch", "Year", "Internship_Company_Name", "Internship_Role", "Internship_Mode", "Internship_Start_Date", "Internship_End_Date", "Stipend_Amount"
    ])
    writer.writeheader()
    writer.writerows(internships)

# 5. Hackathons CSV
hackathons = []
results = ["Winner (1st Place)", "Runner Up (2nd Place)", "Finalist", "Top 10 Finalist", "Special Mention Award"]
for s in students:
    if random.random() < 0.55:
        hack_name, level = random.choice(HACKATHONS)
        team_name = f"Team {s['primary_domain'].split()[0]} Titans"
        hackathons.append({
            "Student_Name": s["student_name"],
            "PRN_or_Roll_No": s["PRN_or_Roll_No"],
            "Hackathon_Name": hack_name,
            "Hackathon_Level": level,
            "Hackathon_Mode": random.choice(["Offline", "Online", "Hybrid"]),
            "Team_Name": team_name,
            "Result_Status": random.choice(results)
        })

with open(os.path.join(OUTPUT_DIR, "hackathons.csv"), "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=[
        "Student_Name", "PRN_or_Roll_No", "Hackathon_Name", "Hackathon_Level", "Hackathon_Mode", "Team_Name", "Result_Status"
    ])
    writer.writeheader()
    writer.writerows(hackathons)

# 6. Certifications CSV
certifications = []
grades = ["Elite + Gold (90%+)", "Elite + Silver (75-89%)", "Elite (60-74%)", "Certificate of Completion", "Grade A+"]
for s in students:
    # Almost all students have 1 or 2 certifications
    for _ in range(random.randint(1, 2)):
        platform = random.choice(PLATFORMS)
        title = f"{platform} Certified: {s['primary_domain']} Fundamentals & Applications"
        certifications.append({
            "Student_Name": s["student_name"],
            "PRN_or_Roll_No": s["PRN_or_Roll_No"],
            "Branch": s["branch"],
            "Year": s["year"],
            "Certification_Title": title,
            "Platform_or_Provider": platform,
            "Certification_Domain": s["primary_domain"],
            "Score_or_Grade": random.choice(grades),
            "Completion_Date": f"2025-{random.randint(1,12):02d}-15"
        })

with open(os.path.join(OUTPUT_DIR, "certifications.csv"), "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=[
        "Student_Name", "PRN_or_Roll_No", "Branch", "Year", "Certification_Title", "Platform_or_Provider", "Certification_Domain", "Score_or_Grade", "Completion_Date"
    ])
    writer.writeheader()
    writer.writerows(certifications)

# 7. Research Papers CSV - Rich domain-specific titles across all departments
DOMAIN_PAPER_TEMPLATES = {
    "Deep Learning": [
        "Contrastive Self-Supervised Learning Framework for Medical Image Segmentation",
        "Transformer-Based Multi-Modal Architecture for Early Disease Diagnosis",
        "Deep Convolutional Neural Networks with Attention Mechanism for Automated Defect Inspection",
        "Transfer Learning Benchmarks across Edge Hardware for Visual Feature Extraction"
    ],
    "Computer Vision": [
        "Real-Time Object Detection and Depth Estimation using Stereo Vision and YOLOv9",
        "Robust Autonomous Drone Navigation under Challenging Illumination via Optical Flow",
        "Facial Landmark Tracking and Emotion Classification on Resource-Constrained Microcontrollers",
        "Multi-Camera Video Surveillance Anomaly Localization using Spatio-Temporal Graph Networks"
    ],
    "NLP & LLMs": [
        "Low-Resource Dialect Fine-Tuning for Indic Languages using Parameter-Efficient Adapters",
        "Retrieval-Augmented Generation for Technical Manuals with Context-Aware Re-Ranking",
        "Quantization and Pruning Strategies for Large Language Models on Consumer Hardware",
        "Automated Fact Verification and Claim Extraction in Scientific Publications using RoBERTa"
    ],
    "Generative AI": [
        "Conditional Diffusion Models for Synthetic Tabular Data Generation in Privacy-Preserving Analytics",
        "Zero-Shot Voice Conversion and Cross-Lingual Speech Synthesis using Latent Diffusion",
        "Code-Completion Agent Architecture with Grounded Semantic Validation",
        "Physics-Informed Generative Adversarial Networks for Fluid Flow Interpolation"
    ],
    "Robotics & Automation": [
        "Kinematic Analysis and Trajectory Optimization for 6-DOF Collaborative Robotic Arm",
        "Autonomous Ground Rover Navigation in Dense Agricultural Canopy using LiDAR and SLAM",
        "Adaptive Impedance Control for Teleoperated Surgical Manipulators with Force Feedback",
        "Model Predictive Control for Autonomous Quadcopter Landing on Moving Marine Platforms"
    ],
    "Electric Vehicles (EV)": [
        "Thermal Runaway Mitigation and Optimal Liquid Cooling for High-Capacity Li-Ion Battery Packs",
        "Regenerative Braking Optimization Strategy for Dual-Motor Light Electric Vehicles",
        "State of Health (SoH) Estimation for EV Batteries using Electrochemical Impedance Spectroscopy and LSTM",
        "Bidirectional V2G (Vehicle-to-Grid) Charging Station Architecture with Grid Synchronization"
    ],
    "Embedded Systems": [
        "Low-Power 32-bit RISC-V Core Implementation with Hardware-Accelerated Cryptographic Extensions",
        "Real-Time Operating System (FreeRTOS) Scheduling Optimization for Automotive Microcontrollers",
        "Fault-Tolerant CAN-FD Communication Protocol for Distributed ECU Subsystems",
        "Energy Harvesting from Piezoelectric Transducers for Self-Powered IoT Nodes"
    ],
    "IoT & Sensor Networks": [
        "Long-Range Precision Soil Telemetry System using LoRaWAN Mesh Architecture",
        "Edge-Enabled Smart Water Metering and Acoustic Leakage Localization Network",
        "Secure Over-The-Air (OTA) Firmware Updates for Constrained IoT Edge Nodes using ChaCha20",
        "Multi-Sensor Environmental Air Quality Monitoring Platform with Cloud Analytics"
    ],
    "Cybersecurity": [
        "Zero-Trust Access Control Framework for Heterogeneous Microservice Deployments",
        "Graph-Based Anomaly Detection for Industrial SCADA and Modbus Protocol Intrusion",
        "Automated Vulnerability Scanning and Penetration Testing via Deep Reinforcement Learning",
        "Post-Quantum Cryptography Implementation on Hardware Security Modules (HSM)"
    ],
    "Cloud Architecture": [
        "Dynamic Auto-Scaling and Predictive Workload Placement in Hybrid Kubernetes Clusters",
        "Cost-Optimal Serverless Function Cold-Start Mitigation using Warm Pool Prediction",
        "Distributed Transaction Management in Multi-Cloud Microservice Ecosystems",
        "Decentralized Object Storage Architecture with Erasure Coding and Zero-Knowledge Encryption"
    ],
    "VLSI Design": [
        "Design of Low-Power 10-bit 200MS/s SAR ADC for Biomedical Sensor Interfaces in 28nm CMOS",
        "Timing and Power Optimization of Cryptographic Hardware Accelerators using High-Level Synthesis",
        "Radiation-Hardened SRAM Cell Architecture for Aerospace Embedded Applications",
        "High-Speed On-Chip Interconnect Router Design for Many-Core System-on-Chip (SoC)"
    ],
    "Green Energy & Biofuels": [
        "Catalytic Pyrolysis of Agricultural Crop Residue Biomass for High-Calorific Bio-Oil",
        "Continuous Transesterification of Waste Cooking Oil to Biodiesel using Heterogeneous Metal Oxides",
        "Experimental Analysis of Perovskite-Silicon Tandem Photovoltaic Cells under Tropical Insolation",
        "Microbial Fuel Cell Optimization for Simultaneous Wastewater Treatment and Power Generation"
    ],
    "Biomedical Instrumentation": [
        "Non-Invasive Continuous Blood Pressure Estimation via Photoplethysmography (PPG) and Wavelet Transforms",
        "Wearable Multi-Channel EMG Sensor Band for Real-Time Prosthetic Hand Actuation",
        "Automated ECG Arrhythmia Detection using 1D Convolutional Neural Networks on Wearables",
        "Design of Impedance Plethysmography System for Pulmonary Function Assessment"
    ],
    "Industrial Automation (PLC/SCADA)": [
        "Design and Deployment of IEC 61131-3 Compliant Batch Process Automation for Food Processing",
        "Digital Twin Modeling of Conveyor Sorting Line for Predictive Maintenance using OPC UA",
        "Safety-Instrumented System (SIS) Design for Chemical Reactor High-Pressure Emergency Shutdown",
        "Closed-Loop Cascade Temperature Control of Heat Exchanger Network using Industrial PAC"
    ],
    "Full Stack Web Development": [
        "Micro-Frontend Architecture for High-Concurrence Enterprise Academic ERP Systems",
        "Real-Time Collaborative Canvas Engine with Operational Transformation and WebSockets",
        "WebAssembly-Powered In-Browser 3D CAD Rendering with Edge Caching",
        "Performance Optimization and Benchmark of Server-Side Rendering vs Static Hydration in Next.js"
    ],
    "Blockchain": [
        "Decentralized Academic Credential Verification Protocol with Soulbound Tokens on Polygon",
        "Smart Contract Automated Escrow System with Formal Verification against Reentrancy Attacks",
        "Zero-Knowledge Rollup Architecture for Scalable Micro-Transactions in Supply Chain",
        "Self-Sovereign Identity (SSI) Management for Inter-University Student Mobility"
    ]
}

research_papers = []
faculty_mentors = [
    "Dr. Rajesh Jalnekar", "Dr. Premanand Ghadekar", "Dr. Shripad Bhatlawande", 
    "Dr. Chandrashekhar Mahajan", "Dr. Ashutosh Marathe", "Dr. Manisha Mali", 
    "Dr. S. T. Patil", "Dr. V. D. Gaikwad", "Dr. K. G. Mundada", "Dr. Snehal Kamalapur"
]

for s in students:
    if (s["cgpa"] >= 8.2 and s["year"] in ("TY", "BTECH")) or random.random() < 0.15:
        venue, pub_type = random.choice(JOURNALS_AND_CONFERENCES)
        domain = s["primary_domain"]
        if domain in DOMAIN_PAPER_TEMPLATES:
            paper_title = random.choice(DOMAIN_PAPER_TEMPLATES[domain])
        else:
            paper_title = f"Design, Optimization and Experimental Evaluation of {domain} using {s['technologies'].split(',')[0]}"
        
        year_pub = random.choice([2024, 2025, 2026])
        doi = f"10.1109/VIT.{year_pub}.{random.randint(1000000, 9999999)}"
        prof_name = random.choice(faculty_mentors)
        authors = f"{s['student_name']}, {prof_name}"
        research_papers.append({
            "Student_Name": s["student_name"],
            "PRN_or_Roll_No": s["PRN_or_Roll_No"],
            "Paper_Title": paper_title,
            "Paper_Domain": domain,
            "Publication_Type": pub_type,
            "Venue_Name": venue,
            "Publication_Status": "Published",
            "Publication_Year": year_pub,
            "DOI_or_Paper_URL": f"https://doi.org/{doi}",
            "Authors": authors,
            "Author_Email": s["email"]
        })

with open(os.path.join(OUTPUT_DIR, "research_papers.csv"), "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=[
        "Student_Name", "PRN_or_Roll_No", "Paper_Title", "Paper_Domain", "Publication_Type", "Venue_Name", "Publication_Status", "Publication_Year", "DOI_or_Paper_URL", "Authors", "Author_Email"
    ])
    writer.writeheader()
    writer.writerows(research_papers)

# 8. Patents and Copyrights CSV - Multi-domain innovation
DOMAIN_PATENT_TEMPLATES = {
    "Robotics & Automation": [
        ("Indian Patent Application", "An Autonomous Agricultural Rover Apparatus with Multispectral Weed Detection and Targeted Spraying"),
        ("Indian Patent Application", "A Modular 6-DOF Collaborative Robotic Gripper with Adaptive Tactile Feedback Mechanism")
    ],
    "Electric Vehicles (EV)": [
        ("Indian Patent Application", "A Regenerative Braking System with Dynamic Supercapacitor Storage for Light Electric Vehicles"),
        ("Indian Patent Application", "A Modular Battery Pack Enclosure with Phase Change Material Thermal Management for EV Two-Wheelers")
    ],
    "IoT & Sensor Networks": [
        ("Indian Patent Application", "A Self-Cleaning Solar-Powered Ultrasonic Water Level and Flow Telemetry Node"),
        ("Indian Patent Application", "An Intelligent Multi-Gas Environmental Monitoring Unit with Automatic Sensor Drift Calibration")
    ],
    "Biomedical Instrumentation": [
        ("Indian Patent Application", "A Wearable Non-Invasive Photoplethysmographic Sensor Band for Continuous Pulse Transit Time Estimation"),
        ("Indian Patent Application", "A Microcontroller-Based Closed-Loop Insulin Infusion Pump with Predictive Glycemic Safety Interlock")
    ],
    "Green Energy & Biofuels": [
        ("Indian Patent Application", "A Continuous Flow Ultrasonic Microreactor for Biodiesel Transesterification from Heterogeneous Feedstocks"),
        ("Indian Patent Application", "An Automated Dust Mitigation and Electrostatic Repulsion Mechanism for Solar Photovoltaic Panels")
    ],
    "Computer Vision": [
        ("Software Copyright Registration", "VisionGuard: Real-Time Industrial Conveyor Belt Surface Defect Inspection Software v3.2"),
        ("Software Copyright Registration", "SignSpeak: Real-Time Indian Sign Language to Speech Translation System v2.0")
    ],
    "NLP & LLMs": [
        ("Software Copyright Registration", "IndicDocAI: Cross-Lingual Academic Document Analysis and Summarization Suite"),
        ("Software Copyright Registration", "AutoGrader: Intelligent Python and C++ Source Code Evaluation Engine with Plagiarism Detection")
    ],
    "Cloud Architecture": [
        ("Software Copyright Registration", "CloudKube: Multi-Cluster Kubernetes Resource Optimizer and Cost Governor Engine"),
        ("Software Copyright Registration", "ZeroShield: Zero-Trust Microservice Gateway and Identity Verification Daemon")
    ],
    "Industrial Automation (PLC/SCADA)": [
        ("Indian Patent Application", "An Intelligent Programmable Logic Interlock for High-Pressure Chemical Reactor Safety Systems"),
        ("Software Copyright Registration", "SCADA-Twin: Industrial OPC-UA Real-Time Simulation and Telemetry Visualizer v1.5")
    ]
}

patents_and_ip = []
for s in students:
    if s["cgpa"] >= 8.5 and random.random() < 0.2:
        domain = s["primary_domain"]
        if domain in DOMAIN_PATENT_TEMPLATES:
            ip_type, ip_title = random.choice(DOMAIN_PATENT_TEMPLATES[domain])
        else:
            if random.random() < 0.6:
                ip_type = "Indian Patent Application"
                ip_title = f"An Apparatus and Intelligent Method for {domain} Monitoring using Embedded System"
            else:
                ip_type = "Software Copyright Registration"
                clean_tech = s['technologies'].split(',')[0].strip().replace(" ", "")
                ip_title = f"{clean_tech}-{domain.split()[0]}Suite: Enterprise {domain} Analytics Engine v2.0"

        if ip_type == "Indian Patent Application":
            reg_no = f"IN/{random.randint(2024, 2026)}/{random.randint(100000, 999999)} A"
            status = random.choice(["Granted", "Published in Patent Office Journal", "Awaiting Examination"])
        else:
            reg_no = f"SW-{random.randint(10000, 99999)}/{random.randint(2024, 2026)}"
            status = "Registered & Certificate Issued"

        patents_and_ip.append({
            "Student_Name": s["student_name"],
            "PRN_or_Roll_No": s["PRN_or_Roll_No"],
            "Branch": s["branch"],
            "Year": s["year"],
            "Title": ip_title,
            "IP_Type": ip_type,
            "Application_or_Registration_No": reg_no,
            "Filing_Status": status,
            "Domain": domain,
            "Filing_Year": random.choice([2024, 2025, 2026])
        })

with open(os.path.join(OUTPUT_DIR, "patents_and_copyrights.csv"), "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=[
        "Student_Name", "PRN_or_Roll_No", "Branch", "Year", "Title", "IP_Type", "Application_or_Registration_No", "Filing_Status", "Domain", "Filing_Year"
    ])
    writer.writeheader()
    writer.writerows(patents_and_ip)

print("Successfully generated:")
print(f"  - Master Students: {len(students)}")
print(f"  - Industry Projects: {len(industry_projects)}")
print(f"  - Academic Projects: {len(academic_projects)}")
print(f"  - Internships: {len(internships)}")
print(f"  - Hackathons: {len(hackathons)}")
print(f"  - Certifications: {len(certifications)}")
print(f"  - Research Papers: {len(research_papers)}")
print(f"  - Patents & Copyrights: {len(patents_and_ip)}")
