import boto3
import os

def lambda_handler(event, context):
    
    # 환경 변수에서 설정값 로드
    cluster_name = os.environ.get('CLUSTER_NAME')
    service_name = os.environ.get('SERVICE_NAME')
    region = os.environ.get('AWS_REGION', 'ap-northeast-2')  # 기본값: 서울 리전
    
    client = boto3.client('ecs', region_name=region)
    
    try:
        # ECS 서비스 업데이트 호출 (강제 새 배포)
        response = client.update_service(
            cluster=cluster_name,
            service=service_name,
            desiredCount=1,
          
            forceNewDeployment=True
        )
        
        print(f"Successfully triggered restart for service: {service_name}")
        return {
            'statusCode': 200,
            'body': f"Service {service_name} is restarting..."
        }
        
    except Exception as e:
        print(f"Error updating service: {str(e)}")
        return {
            'statusCode': 500,
            'body': "Error updating ECS service"
        }