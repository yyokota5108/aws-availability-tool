# Application Load Balancerの作成
resource "aws_lb" "main" {
  name               = "${var.project}-${var.environment}-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [var.security_group_id]
  subnets            = var.public_subnet_ids

  enable_deletion_protection = false

  tags = merge(
    {
      Name        = "${var.project}-${var.environment}-alb"
      Environment = var.environment
      Project     = var.project
    },
    var.tags
  )
}

# ターゲットグループの作成
resource "aws_lb_target_group" "main" {
  name        = "${var.project}-${var.environment}-tg"
  port        = var.target_group_port
  protocol    = "HTTP"
  vpc_id      = var.vpc_id
  target_type = "instance"

  health_check {
    enabled             = true
    healthy_threshold   = 2
    interval            = 30
    matcher             = "200"
    path                = var.health_check_path
    port                = "traffic-port"
    protocol            = "HTTP"
    timeout             = 5
    unhealthy_threshold = 2
  }

  tags = merge(
    {
      Name        = "${var.project}-${var.environment}-tg"
      Environment = var.environment
      Project     = var.project
    },
    var.tags
  )

  lifecycle {
    create_before_destroy = true
  }
}

# リスナーの作成
resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.main.arn
  port              = "80"
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.main.arn
  }
}
